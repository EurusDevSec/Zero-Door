package guard

import (
	"fmt"
	"os"
	"regexp"
	"slices"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
)

type Policy struct {
	Version        string              `json:"version"`
	Enabled        bool                `json:"enabled"`
	Context        attack.RunContext   `json:"context"`
	Targets        []validation.Target `json:"targets"`
	MaxDurationSec int                 `json:"maxDurationSec"`
	MaxConcurrency int                 `json:"maxConcurrency"`
	RPS            int                 `json:"rps"`
}

var uuidID = regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`)
var runID = regexp.MustCompile(`^run_[0-9a-f]{32}$`)
var trialID = regexp.MustCompile(`^trl_[0-9a-f]{32}$`)

func LoadPolicy(path string) (Policy, error) {
	var p Policy
	data, err := os.ReadFile(path) // #nosec G304 -- Read-only path from trusted process configuration, never a request/message.
	if err != nil {
		return p, err
	}
	if err = attack.StrictJSON(data, &p); err != nil {
		return p, err
	}
	return p, p.Validate()
}
func (p Policy) Validate() error {
	if p.Version != "zd-guard/1" || !runID.MatchString(p.Context.RunID) || !trialID.MatchString(p.Context.TrialID) ||
		!slices.Contains([]string{"B0", "BM", "B1", "B2", "B3"}, p.Context.Group) ||
		len(p.Targets) == 0 || p.MaxDurationSec < 1 || p.MaxDurationSec > 600 || p.MaxConcurrency < 1 || p.MaxConcurrency > 50 || p.RPS < 1 || p.RPS > 100 {
		return fmt.Errorf("POLICY_CONFIG")
	}
	v := validation.New([]string{"target-app"})
	seen := map[string]bool{}
	for _, t := range p.Targets {
		id := t.Namespace + "/" + t.Service
		if seen[id] {
			return fmt.Errorf("POLICY_DUPLICATE_TARGET")
		}
		seen[id] = true
		if _, err := v.Resolve(t.Namespace, t.Service, "", false); err != nil {
			return err
		}
		if t.URL != "" {
			if _, err := v.Resolve(t.Namespace, t.Service, t.URL, true); err != nil {
				return err
			}
		}
	}
	return nil
}

func (p Policy) Admit(cmd attack.AttackCommand) (attack.AttackCommand, error) {
	if err := p.Validate(); err != nil {
		return cmd, err
	}
	if cmd.Context != p.Context {
		return cmd, fmt.Errorf("RUN_CONTEXT")
	}
	if _, err := time.Parse(time.RFC3339Nano, cmd.Timestamp); err != nil {
		return cmd, fmt.Errorf("COMMAND_TIMESTAMP")
	}
	if !uuidID.MatchString(cmd.CommandID) || cmd.Source != "nemesis" {
		return cmd, fmt.Errorf("COMMAND_ID_OR_SOURCE")
	}
	if !slices.Contains([]string{"HTTP_FLOOD", "CPU_STRESS", "MEMORY_STRESS", "POD_KILL"}, cmd.AttackType) {
		return cmd, fmt.Errorf("COMMAND_TYPE")
	}
	if !slices.Contains([]string{"LOW", "MEDIUM", "HIGH"}, cmd.Parameters.Intensity) || cmd.Parameters.Concurrency < 1 || cmd.Parameters.Concurrency > 10000 || cmd.Parameters.DurationSec < 1 || cmd.Parameters.DurationSec > 86400 || cmd.SafetyLimits.MaxDurationSec < 1 || cmd.SafetyLimits.MaxDurationSec > 86400 {
		return cmd, fmt.Errorf("COMMAND_LIMIT")
	}
	if len(cmd.SafetyLimits.AllowedNamespaces) != 1 || cmd.SafetyLimits.AllowedNamespaces[0] != "target-app" {
		return cmd, fmt.Errorf("COMMAND_NAMESPACE_LIMIT")
	}
	if len(cmd.Parameters.CustomParams) != 0 {
		return cmd, fmt.Errorf("CUSTOM_PARAMETER")
	}
	v := validation.NewWithTargets([]string{"target-app"}, p.Targets)
	url, err := v.Resolve(cmd.Target.Namespace, cmd.Target.Service, cmd.Target.URL, cmd.AttackType == "HTTP_FLOOD")
	if err != nil {
		return cmd, err
	}
	cmd.Target.URL = url
	duration := attack.EffectiveDuration(cmd, p.MaxDurationSec)
	if duration <= 0 {
		return cmd, fmt.Errorf("DURATION")
	}
	cmd.Parameters.DurationSec = int(duration.Seconds())
	cmd.SafetyLimits.MaxDurationSec = p.MaxDurationSec
	if cmd.Parameters.Concurrency > p.MaxConcurrency {
		cmd.Parameters.Concurrency = p.MaxConcurrency
	}
	// B0 permits planned harness faults; this purpose grants no healing or LLM authority.
	return cmd, nil
}
