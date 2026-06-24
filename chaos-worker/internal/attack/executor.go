// Package attack defines the shared types and executor interface for all attack implementations.
package attack

import (
	"context"
	"encoding/json"
	"time"
)

// ---- Kafka Message Schemas ----

// AttackTarget is the target specification inside an AttackCommand.
type AttackTarget struct {
	Namespace string `json:"namespace"`
	Service   string `json:"service"`
	URL       string `json:"url,omitempty"` // optional, only for HTTP attacks
}

// AttackParameters holds configurable attack parameters.
type AttackParameters struct {
	DurationSec  int            `json:"duration"`    // seconds to run the attack
	Intensity    string         `json:"intensity"`   // LOW | MEDIUM | HIGH
	Concurrency  int            `json:"concurrency"` // concurrent goroutines/workers
	CustomParams map[string]any `json:"customParams,omitempty"`
}

// SafetyLimits are kill-switch values sent from Nemesis.
type SafetyLimits struct {
	MaxDurationSec    int      `json:"maxDuration"`
	AllowedNamespaces []string `json:"allowedNamespaces"`
}

// AttackCommand is the message schema consumed from topic `attack.commands`.
type AttackCommand struct {
	CommandID   string           `json:"commandId"`
	Timestamp   string           `json:"timestamp"`
	Source      string           `json:"source"`
	AttackType  string           `json:"attackType"` // HTTP_FLOOD | CPU_STRESS | MEMORY_STRESS | POD_KILL
	Target      AttackTarget     `json:"target"`
	Parameters  AttackParameters `json:"parameters"`
	SafetyLimits SafetyLimits   `json:"safetyLimits"`
}

// AttackResult is the message schema produced to topic `attack.results`.
type AttackResult struct {
	ResultID    string        `json:"resultId"`
	CommandID   string        `json:"commandId"`
	Timestamp   string        `json:"timestamp"`
	Source      string        `json:"source"`
	Status      string        `json:"status"`      // SUCCESS | FAILED | REJECTED | TIMEOUT
	AttackType  string        `json:"attackType"`
	DurationMs  int64         `json:"duration"`    // actual execution time in ms
	Details     ResultDetails `json:"details"`
}

// ResultDetails holds attack-specific outcome metadata.
type ResultDetails struct {
	RequestsSent int    `json:"requestsSent,omitempty"`
	PodsKilled   int    `json:"podsKilled,omitempty"`
	ErrorMessage string `json:"errorMessage,omitempty"`
}

// ---- Executor Interface ----

// Executor is the interface that every attack type must implement.
type Executor interface {
	Execute(ctx context.Context, cmd AttackCommand) AttackResult
}

// ---- Helpers ----

// ParseCommand deserialises a raw JSON byte slice into an AttackCommand.
func ParseCommand(data []byte) (AttackCommand, error) {
	var cmd AttackCommand
	err := json.Unmarshal(data, &cmd)
	return cmd, err
}

// NowISO returns the current UTC time formatted as ISO 8601.
func NowISO() string {
	return time.Now().UTC().Format(time.RFC3339Nano)
}

// EffectiveDuration returns the lower of the command duration and the
// global max-duration kill-switch, ensuring we never exceed safety limits.
func EffectiveDuration(cmd AttackCommand, globalMaxSec int) time.Duration {
	d := cmd.Parameters.DurationSec
	maxD := cmd.SafetyLimits.MaxDurationSec
	if maxD <= 0 {
		maxD = globalMaxSec
	}
	if d <= 0 || d > maxD {
		d = maxD
	}
	return time.Duration(d) * time.Second
}
