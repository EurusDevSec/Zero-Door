package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Config holds all runtime configuration for the Chaos Worker.
type Config struct {
	Error      error
	PolicyFile string
	SignerFile string
	LedgerDir  string
	// Kafka
	KafkaBootstrapServers string
	KafkaGroupID          string
	KafkaCommandsTopic    string
	KafkaResultsTopic     string

	// Kubernetes
	KubeInCluster bool   // true when running inside K8s pod
	KubeConfig    string // path to kubeconfig (only used when NOT in-cluster)

	// Safety limits
	AllowedNamespaces []string
	MaxDurationSec    int // Global kill switch: max seconds for any single attack

	// HTTP Flood defaults
	DefaultConcurrency int
	DefaultRPS         int
}

// Load reads configuration from environment variables.
func Load() *Config {
	var configErr error
	maxDur := 60
	if v := os.Getenv("MAX_ATTACK_DURATION_SEC"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 && n <= 600 {
			maxDur = n
		} else {
			configErr = fmt.Errorf("INVALID_MAX_DURATION")
		}
	}

	concurrency := 2
	if v := os.Getenv("DEFAULT_CONCURRENCY"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 && n <= 50 {
			concurrency = n
		} else {
			configErr = fmt.Errorf("INVALID_CONCURRENCY")
		}
	}

	rps := 5
	if v := os.Getenv("DEFAULT_RPS"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 && n <= 100 {
			rps = n
		} else {
			configErr = fmt.Errorf("INVALID_RPS")
		}
	}

	allowedNS := []string{"target-app"}
	if v := os.Getenv("ALLOWED_NAMESPACES"); v != "" {
		allowedNS = strings.Split(v, ",")
		if len(allowedNS) != 1 || allowedNS[0] != "target-app" {
			configErr = fmt.Errorf("INVALID_NAMESPACE_LIMIT")
		}
	}

	return &Config{
		Error:                 configErr,
		PolicyFile:            os.Getenv("ZD_COMMAND_POLICY_FILE"),
		SignerFile:            os.Getenv("ZD_COMMAND_SIGNER_FILE"),
		LedgerDir:             os.Getenv("ZD_COMMAND_LEDGER_DIR"),
		KafkaBootstrapServers: getEnvOrDefault("KAFKA_BOOTSTRAP_SERVERS", "kafka.zero-door.svc.cluster.local:9092"),
		KafkaGroupID:          getEnvOrDefault("KAFKA_GROUP_ID", "chaos-worker-group"),
		KafkaCommandsTopic:    getEnvOrDefault("KAFKA_COMMANDS_TOPIC", "attack.commands"),
		KafkaResultsTopic:     getEnvOrDefault("KAFKA_RESULTS_TOPIC", "attack.results"),
		KubeInCluster:         os.Getenv("KUBERNETES_SERVICE_HOST") != "",
		KubeConfig:            os.Getenv("KUBECONFIG"),
		AllowedNamespaces:     allowedNS,
		MaxDurationSec:        maxDur,
		DefaultConcurrency:    concurrency,
		DefaultRPS:            rps,
	}
}

func getEnvOrDefault(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}
