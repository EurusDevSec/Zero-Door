package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
	kafkaclient "github.com/eurusdevsec/zero-door/chaos-worker/internal/kafka"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/config"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
	"github.com/google/uuid"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

func main() {
	// Structured JSON logging (production-ready)
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	})))

	slog.Info("Zero Door Chaos Worker starting up...")

	cfg := config.Load()
	slog.Info("Configuration loaded",
		"kafkaBrokers", cfg.KafkaBootstrapServers,
		"commandsTopic", cfg.KafkaCommandsTopic,
		"resultsTopic", cfg.KafkaResultsTopic,
		"allowedNamespaces", cfg.AllowedNamespaces,
		"maxDurationSec", cfg.MaxDurationSec,
	)

	// ---- Build Kubernetes client ----
	kubeClient, err := buildKubeClient(cfg)
	if err != nil {
		slog.Error("Failed to build Kubernetes client", "error", err)
		os.Exit(1)
	}

	// ---- Blast radius validator ----
	validator := validation.New(cfg.AllowedNamespaces)

	// ---- Kafka consumer ----
	consumer, err := kafkaclient.NewConsumer(cfg.KafkaBootstrapServers, cfg.KafkaGroupID, cfg.KafkaCommandsTopic)
	if err != nil {
		slog.Error("Failed to create Kafka consumer", "error", err)
		os.Exit(1)
	}
	defer consumer.Close()

	// ---- Kafka producer ----
	producer, err := kafkaclient.NewProducer(cfg.KafkaBootstrapServers, cfg.KafkaResultsTopic)
	if err != nil {
		slog.Error("Failed to create Kafka producer", "error", err)
		os.Exit(1)
	}
	defer producer.Close()

	// ---- Build executor registry ----
	executors := map[string]attack.Executor{
		"HTTP_FLOOD": &attack.HTTPFloodExecutor{
			MaxConcurrency: cfg.DefaultConcurrency,
			GlobalMaxSec:   cfg.MaxDurationSec,
		},
		"CPU_STRESS": &attack.CPUStressExecutor{
			KubeClient:   kubeClient,
			GlobalMaxSec: cfg.MaxDurationSec,
		},
		"MEMORY_STRESS": &attack.CPUStressExecutor{ // reuses stress pod, just with more vm workers
			KubeClient:   kubeClient,
			GlobalMaxSec: cfg.MaxDurationSec,
		},
		"POD_KILL": &attack.PodKillExecutor{
			KubeClient:   kubeClient,
			GlobalMaxSec: cfg.MaxDurationSec,
		},
	}

	// ---- Graceful shutdown ----
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	slog.Info("Chaos Worker is ready. Listening for attack commands on Kafka...",
		"topic", cfg.KafkaCommandsTopic,
	)

	// ---- Main event loop ----
	for {
		select {
		case <-ctx.Done():
			slog.Info("Shutdown signal received. Stopping Chaos Worker gracefully...")
			producer.Flush(10000)
			return

		default:
			raw, err := consumer.Poll(ctx, 1000) // 1s poll timeout
			if err != nil {
				if err == context.Canceled {
					return
				}
				slog.Error("Kafka poll error", "error", err)
				time.Sleep(2 * time.Second) // back-off before retry
				continue
			}
			if raw == nil {
				continue // no message available
			}

			// Parse the command
			cmd, err := attack.ParseCommand(raw)
			if err != nil {
				slog.Error("Failed to deserialise AttackCommand", "error", err, "raw", string(raw))
				continue
			}

			slog.Info("Attack command received",
				"commandId", cmd.CommandID,
				"type", cmd.AttackType,
				"target", cmd.Target.Namespace+"/"+cmd.Target.Service,
			)

			// Validate blast radius — BEFORE executing anything
			if err := validator.ValidateNamespace(cmd.Target.Namespace); err != nil {
				slog.Error("Attack REJECTED by blast radius validator", "commandId", cmd.CommandID, "reason", err)
				result := attack.AttackResult{
					ResultID:   uuid.New().String(),
					CommandID:  cmd.CommandID,
					Timestamp:  attack.NowISO(),
					Source:     "chaos-worker",
					Status:     "REJECTED",
					AttackType: cmd.AttackType,
					DurationMs: 0,
					Details:    attack.ResultDetails{ErrorMessage: err.Error()},
				}
				if sendErr := producer.Send(result); sendErr != nil {
					slog.Error("Failed to publish REJECTED result", "error", sendErr)
				}
				continue
			}

			if err := validator.ValidateURL(cmd.Target.URL); err != nil {
				slog.Error("Attack REJECTED — URL validation failed", "commandId", cmd.CommandID, "reason", err)
				result := attack.AttackResult{
					ResultID:   uuid.New().String(),
					CommandID:  cmd.CommandID,
					Timestamp:  attack.NowISO(),
					Source:     "chaos-worker",
					Status:     "REJECTED",
					AttackType: cmd.AttackType,
					DurationMs: 0,
					Details:    attack.ResultDetails{ErrorMessage: err.Error()},
				}
				if sendErr := producer.Send(result); sendErr != nil {
					slog.Error("Failed to publish REJECTED result", "error", sendErr)
				}
				continue
			}

			// Look up executor
			executor, ok := executors[cmd.AttackType]
			if !ok {
				slog.Warn("Unknown attack type — skipping", "attackType", cmd.AttackType, "commandId", cmd.CommandID)
				result := attack.AttackResult{
					ResultID:   uuid.New().String(),
					CommandID:  cmd.CommandID,
					Timestamp:  attack.NowISO(),
					Source:     "chaos-worker",
					Status:     "REJECTED",
					AttackType: cmd.AttackType,
					DurationMs: 0,
					Details:    attack.ResultDetails{ErrorMessage: "Unsupported attack type: " + cmd.AttackType},
				}
				if sendErr := producer.Send(result); sendErr != nil {
					slog.Error("Failed to publish REJECTED result", "error", sendErr)
				}
				continue
			}

			// Execute the attack in a goroutine so the event loop remains responsive
			go func(c attack.AttackCommand, ex attack.Executor) {
				attackCtx, cancel := context.WithTimeout(context.Background(),
					time.Duration(cfg.MaxDurationSec+10)*time.Second,
				)
				defer cancel()

				result := ex.Execute(attackCtx, c)

				if sendErr := producer.Send(result); sendErr != nil {
					slog.Error("Failed to publish attack result", "commandId", c.CommandID, "error", sendErr)
				} else {
					slog.Info("Attack result published",
						"commandId", c.CommandID,
						"status", result.Status,
						"durationMs", result.DurationMs,
					)
				}
			}(cmd, executor)
		}
	}
}

// buildKubeClient creates a Kubernetes client, using in-cluster config if running inside a pod,
// or kubeconfig from file/env if running locally.
func buildKubeClient(cfg *config.Config) (kubernetes.Interface, error) {
	var restCfg *rest.Config
	var err error

	if cfg.KubeInCluster {
		slog.Info("Using in-cluster Kubernetes config")
		restCfg, err = rest.InClusterConfig()
	} else {
		kubeconfig := cfg.KubeConfig
		if kubeconfig == "" {
			kubeconfig = clientcmd.RecommendedHomeFile // ~/.kube/config
		}
		slog.Info("Using kubeconfig file", "path", kubeconfig)
		restCfg, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
	}

	if err != nil {
		return nil, err
	}

	return kubernetes.NewForConfig(restCfg)
}
