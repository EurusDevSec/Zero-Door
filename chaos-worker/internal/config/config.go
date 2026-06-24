package config

import (
	"os"
	"strconv"
	"strings"
)

// Config holds all runtime configuration for the Chaos Worker.
type Config struct {
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
	maxDur := 120
	if v := os.Getenv("MAX_ATTACK_DURATION_SEC"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 {
			maxDur = n
		}
	}

	concurrency := 50
	if v := os.Getenv("DEFAULT_CONCURRENCY"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 {
			concurrency = n
		}
	}

	rps := 100
	if v := os.Getenv("DEFAULT_RPS"); v != "" {
		if n, err := strconv.Atoi(v); err == nil && n > 0 {
			rps = n
		}
	}

	allowedNS := []string{"target-app"}
	if v := os.Getenv("ALLOWED_NAMESPACES"); v != "" {
		allowedNS = strings.Split(v, ",")
	}

	return &Config{
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
