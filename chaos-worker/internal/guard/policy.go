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
	// SQLi is an opt-in capability, absent (nil) by default so SQLI commands are refused unless a policy
	// explicitly enables it and locks the single fixture endpoint. It never widens the legacy targets above.
	SQLi *SQLiCapability `json:"sqli,omitempty"`
}

// SQLiCapability pins the SQLi executor to one fixture endpoint. Endpoint is the exact base search URL; the
// executor only appends the `category` parameter it builds from the locked catalog. MaxSends/MaxCommandSec may
// lower the design ceilings (attack.SQLiMaxSends / attack.SQLiPerCommandSec), never raise them.
type SQLiCapability struct {
	Enabled       bool   `json:"enabled"`
	Endpoint      string `json:"endpoint"`
	MaxSends      int    `json:"maxSends"`
	MaxCommandSec int    `json:"maxCommandSec"`
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
	if p.SQLi != nil {
		if _, err := validation.ValidateSQLiEndpoint(p.SQLi.Endpoint); err != nil {
			return err
		}
		if p.SQLi.MaxSends < 1 || p.SQLi.MaxSends > attack.SQLiMaxSends ||
			p.SQLi.MaxCommandSec < 1 || p.SQLi.MaxCommandSec > attack.SQLiPerCommandSec {
			return fmt.Errorf("SQLI_POLICY")
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
	// SQLI is admitted on a separate, additive branch so the legacy checks below (target-app resolution,
	// empty customParams) stay exactly as they were for the four original command types.
	if cmd.AttackType == "SQLI" {
		return p.admitSQLi(cmd)
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

// admitSQLi admits one SQLI command. It requires the opt-in capability, locks the target to the single
// configured fixture endpoint, fixes concurrency to one, clamps the duration to the capability ceiling, and
// accepts customParams holding exactly {"template": "<known catalog id>"}. The legacy executors can never be
// routed to the fixture, because they resolve targets through validation.New (target-app only) and are never
// reached from this branch.
func (p Policy) admitSQLi(cmd attack.AttackCommand) (attack.AttackCommand, error) {
	if p.SQLi == nil || !p.SQLi.Enabled {
		return cmd, fmt.Errorf("SQLI_DISABLED")
	}
	if cmd.Target.Namespace != attack.SQLiNamespace || cmd.Target.Service != attack.SQLiService {
		return cmd, fmt.Errorf("SQLI_TARGET")
	}
	endpoint, err := validation.ValidateSQLiEndpoint(cmd.Target.URL)
	if err != nil {
		return cmd, err
	}
	allowed, err := validation.ValidateSQLiEndpoint(p.SQLi.Endpoint)
	if err != nil || endpoint != allowed {
		return cmd, fmt.Errorf("SQLI_ENDPOINT_NOT_ALLOWED")
	}
	cmd.Target.URL = endpoint
	if cmd.Parameters.Concurrency != attack.SQLiConcurrency {
		return cmd, fmt.Errorf("SQLI_CONCURRENCY")
	}
	if cmd.Parameters.Intensity != "LOW" {
		return cmd, fmt.Errorf("SQLI_INTENSITY")
	}
	maxSec := min(p.SQLi.MaxCommandSec, attack.SQLiPerCommandSec)
	if cmd.Parameters.DurationSec < 1 || cmd.Parameters.DurationSec > maxSec {
		return cmd, fmt.Errorf("SQLI_DURATION")
	}
	if len(cmd.SafetyLimits.AllowedNamespaces) != 1 || cmd.SafetyLimits.AllowedNamespaces[0] != attack.SQLiNamespace {
		return cmd, fmt.Errorf("SQLI_NAMESPACE_LIMIT")
	}
	if cmd.SafetyLimits.MaxDurationSec < 1 || cmd.SafetyLimits.MaxDurationSec > attack.SQLiPerCommandSec {
		return cmd, fmt.Errorf("SQLI_SAFETY_LIMIT")
	}
	if _, err := sqliTemplateParam(cmd.Parameters.CustomParams); err != nil {
		return cmd, err
	}
	return cmd, nil
}

// sqliTemplateParam accepts customParams holding exactly one key "template" whose string value is a known
// catalog id. Any other key, a missing key, a non-string value, or an unknown id is refused. Legacy command
// types keep rejecting customParams entirely (the CUSTOM_PARAMETER check on the legacy branch is unchanged).
func sqliTemplateParam(cp map[string]any) (attack.SQLiTemplate, error) {
	if len(cp) != 1 {
		return attack.SQLiTemplate{}, fmt.Errorf("SQLI_CUSTOM_PARAM")
	}
	raw, ok := cp["template"]
	if !ok {
		return attack.SQLiTemplate{}, fmt.Errorf("SQLI_CUSTOM_PARAM")
	}
	id, ok := raw.(string)
	if !ok {
		return attack.SQLiTemplate{}, fmt.Errorf("SQLI_TEMPLATE_TYPE")
	}
	tmpl, ok := attack.LookupSQLiTemplate(id)
	if !ok {
		return attack.SQLiTemplate{}, fmt.Errorf("SQLI_TEMPLATE_UNKNOWN")
	}
	return tmpl, nil
}
