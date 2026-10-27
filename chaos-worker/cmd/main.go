package main

import (
	"context"
	"log/slog"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/config"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/guard"
	kafkaclient "github.com/eurusdevsec/zero-door/chaos-worker/internal/kafka"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

func main() { os.Exit(run()) }

func run() int {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	return runWithContext(ctx)
}

func runWithContext(ctx context.Context) int {
	// Structured JSON logging (production-ready)
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	})))

	slog.Info("Zero Door Chaos Worker starting up...")

	cfg := config.Load()
	if cfg.Error != nil {
		slog.Error("Invalid operational limits", "error", cfg.Error)
		return 1
	}
	policy, err := guard.LoadPolicy(cfg.PolicyFile)
	if err != nil {
		slog.Error("Guard policy unavailable", "error", err)
		return 1
	}
	if cfg.MaxDurationSec < policy.MaxDurationSec {
		policy.MaxDurationSec = cfg.MaxDurationSec
	}
	if cfg.DefaultConcurrency < policy.MaxConcurrency {
		policy.MaxConcurrency = cfg.DefaultConcurrency
	}
	if cfg.DefaultRPS < policy.RPS {
		policy.RPS = cfg.DefaultRPS
	}
	if !policy.Enabled {
		slog.Info("EXECUTOR_DISABLED: waiting for shutdown without opening clients or ledger")
		<-ctx.Done()
		return 0
	}
	var sqliIP net.IP
	if policy.SQLi != nil && policy.SQLi.Enabled {
		sqliIP = net.ParseIP(os.Getenv("ZD_SQLI_INGRESS_IP"))
		if sqliIP == nil || !sqliIP.IsPrivate() || sqliIP.IsLoopback() || sqliIP.IsLinkLocalUnicast() {
			slog.Error("SQLI enabled without a valid operator-pinned private ingress Service IP")
			return 1
		}
	}
	key, err := guard.LoadKey(cfg.SignerFile)
	if err != nil {
		slog.Error("Signer configuration unavailable")
		return 1
	}
	ledger, err := guard.OpenLedger(cfg.LedgerDir)
	if err != nil {
		slog.Error("Durable ledger unavailable", "error", err)
		return 1
	}
	defer ledger.Close()
	kubeClient, err := buildKubeClient(cfg)
	if err != nil {
		slog.Error("Kubernetes client unavailable", "error", err)
		return 1
	}

	// ---- Kafka consumer ----
	consumer, err := kafkaclient.NewConsumer(cfg.KafkaBootstrapServers, cfg.KafkaGroupID, cfg.KafkaCommandsTopic)
	if err != nil {
		slog.Error("Failed to create Kafka consumer", "error", err)
		return 1
	}
	defer consumer.Close()

	// ---- Kafka producer ----
	producer, err := kafkaclient.NewProducer(cfg.KafkaBootstrapServers, cfg.KafkaResultsTopic)
	if err != nil {
		slog.Error("Failed to create Kafka producer", "error", err)
		return 1
	}
	defer producer.Close()

	// ---- Build executor registry ----
	executors := map[string]attack.Executor{
		"HTTP_FLOOD": &attack.HTTPFloodExecutor{
			MaxConcurrency: policy.MaxConcurrency,
			MaxRPS:         policy.RPS,
			MaxRequests:    policy.RPS * policy.MaxDurationSec,
			GlobalMaxSec:   policy.MaxDurationSec,
		},
		"CPU_STRESS": &attack.CPUStressExecutor{
			KubeClient:   kubeClient,
			GlobalMaxSec: policy.MaxDurationSec,
		},
		"MEMORY_STRESS": &attack.CPUStressExecutor{ // reuses stress pod, just with more vm workers
			KubeClient:   kubeClient,
			GlobalMaxSec: policy.MaxDurationSec,
		},
		"POD_KILL": &attack.PodKillExecutor{
			KubeClient:   kubeClient,
			GlobalMaxSec: policy.MaxDurationSec,
		},
	}
	// The SQLi executor is registered only when the opt-in capability is enabled. It sends HTTP to the fixture
	// endpoint and needs no Kubernetes client; admission already refuses SQLI when the capability is absent.
	if policy.SQLi != nil && policy.SQLi.Enabled {
		executors["SQLI"] = &attack.SQLIExecutor{MaxSends: policy.SQLi.MaxSends, MaxCommandSec: policy.SQLi.MaxCommandSec, ApprovedIP: sqliIP}
	}

	slog.Info("Chaos Worker is ready. Listening for attack commands on Kafka...",
		"topic", cfg.KafkaCommandsTopic,
	)

	dispatcher := &guard.Dispatcher{Policy: policy, Key: key, Ledger: ledger, Executors: executors}
	return consumeCommands(ctx, consumer, producer, dispatcher, ledger.Failure)
}

type commandConsumer interface {
	Poll(context.Context, int) ([]byte, error)
	Ack(context.Context) error
}
type resultProducer interface{ Send(any) error }
type commandHandler interface {
	Handle(context.Context, []byte) (attack.AttackResult, error)
}

// consumeCommands preserves Handle -> durable state -> Send -> Ack ordering.
// Producer.Send owns a fresh 10s context. Ack must also outlive cancellation of
// the executor, otherwise every graceful stop forces unnecessary redelivery.
func consumeCommands(ctx context.Context, consumer commandConsumer, producer resultProducer, dispatcher commandHandler, failure func() error) int {
	// Serial dispatch bounds aggregate commands and waits for owned cleanup before shutdown.
	for ctx.Err() == nil {
		raw, err := consumer.Poll(ctx, 1000)
		if err != nil {
			slog.Error("Kafka poll failed", "error", err)
			return 1
		}
		if raw == nil {
			continue
		}
		result, admissionErr := dispatcher.Handle(ctx, raw)
		if err = failure(); err != nil {
			slog.Error("Ledger failed; refusing further consumption", "error", err)
			return 1
		}
		if admissionErr != nil {
			slog.Warn("Command refused or failed", "reason", admissionErr.Error())
		}
		// On any unknown persistence/publish/commit outcome, stop. Redelivery never repeats a claimed effect.
		if err = producer.Send(result); err != nil {
			slog.Error("Result publication failed", "error", err)
			return 1
		}
		ackCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		err = consumer.Ack(ackCtx)
		cancel()
		if err != nil {
			slog.Error("Offset acknowledgement failed", "error", err)
			return 1
		}
	}
	return 0
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
