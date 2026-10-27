package guard

import (
	"os"
	"strings"
	"testing"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
)

// A representative in-cluster endpoint. The real production value is the private ingress address set in the
// lab-approved config; admission only cares that a command's URL equals this one exactly.
const sqliEndpoint = "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search"

func sqliPolicy() Policy {
	ctx := attack.RunContext{RunID: "run_" + strings.Repeat("1", 32), TrialID: "trl_" + strings.Repeat("2", 32), Group: "B1"}
	return Policy{
		Version: "zd-guard/1", Enabled: true, Context: ctx,
		Targets:        []validation.Target{{Namespace: "target-app", Service: "frontend", URL: "http://frontend.target-app.svc.cluster.local/"}},
		MaxDurationSec: 30, MaxConcurrency: 2, RPS: 5,
		SQLi: &SQLiCapability{Enabled: true, Endpoint: sqliEndpoint, MaxSends: 20, MaxCommandSec: 30},
	}
}

func sqliCommand(ctx attack.RunContext) attack.AttackCommand {
	return attack.AttackCommand{
		CommandID:  "11111111-1111-4111-8111-111111111111",
		Timestamp:  "2023-11-14T22:13:20Z",
		Source:     "nemesis",
		Context:    ctx,
		AttackType: "SQLI",
		Target:     attack.AttackTarget{Namespace: "zd-sqli-lab", Service: "sqli-fixture", URL: sqliEndpoint},
		Parameters: attack.AttackParameters{DurationSec: 30, Intensity: "LOW", Concurrency: 1,
			CustomParams: map[string]any{"template": "disclose-restricted"}},
		SafetyLimits: attack.SafetyLimits{MaxDurationSec: 30, AllowedNamespaces: []string{"zd-sqli-lab"}},
	}
}

func TestAdmitSQLiValid(t *testing.T) {
	p := sqliPolicy()
	c := sqliCommand(p.Context)
	out, err := p.Admit(c)
	if err != nil {
		t.Fatal("valid SQLi command refused:", err)
	}
	if out.Target.URL != sqliEndpoint {
		t.Fatalf("endpoint not canonicalised: %q", out.Target.URL)
	}
	c.Parameters.CustomParams = map[string]any{"template": "benign-apparel"}
	if _, err := p.Admit(c); err != nil {
		t.Fatal("benign control refused:", err)
	}
}

func TestAdmitSQLiRejections(t *testing.T) {
	for name, change := range map[string]func(*Policy, *attack.AttackCommand){
		"disabled":          func(p *Policy, c *attack.AttackCommand) { p.SQLi.Enabled = false },
		"capability-absent": func(p *Policy, c *attack.AttackCommand) { p.SQLi = nil },
		"wrong-namespace":   func(p *Policy, c *attack.AttackCommand) { c.Target.Namespace = "target-app" },
		"wrong-service":     func(p *Policy, c *attack.AttackCommand) { c.Target.Service = "frontend" },
		"endpoint-host-mismatch": func(p *Policy, c *attack.AttackCommand) {
			c.Target.URL = "http://evil.zd-sqli-lab.svc.cluster.local/fixture/catalog/search"
		},
		"endpoint-with-query": func(p *Policy, c *attack.AttackCommand) { c.Target.URL = sqliEndpoint + "?category=x" },
		"endpoint-wrong-path": func(p *Policy, c *attack.AttackCommand) {
			c.Target.URL = "http://sqli-fixture.zd-sqli-lab.svc.cluster.local/fixture/orders"
		},
		"concurrency-2":            func(p *Policy, c *attack.AttackCommand) { c.Parameters.Concurrency = 2 },
		"intensity-high":           func(p *Policy, c *attack.AttackCommand) { c.Parameters.Intensity = "HIGH" },
		"duration-over":            func(p *Policy, c *attack.AttackCommand) { c.Parameters.DurationSec = 31 },
		"duration-zero":            func(p *Policy, c *attack.AttackCommand) { c.Parameters.DurationSec = 0 },
		"duration-over-policy-cap": func(p *Policy, c *attack.AttackCommand) { p.SQLi.MaxCommandSec = 10; c.Parameters.DurationSec = 11 },
		"ns-limit-targetapp":       func(p *Policy, c *attack.AttackCommand) { c.SafetyLimits.AllowedNamespaces = []string{"target-app"} },
		"ns-limit-two": func(p *Policy, c *attack.AttackCommand) {
			c.SafetyLimits.AllowedNamespaces = []string{"zd-sqli-lab", "target-app"}
		},
		"safety-over":  func(p *Policy, c *attack.AttackCommand) { c.SafetyLimits.MaxDurationSec = 31 },
		"custom-empty": func(p *Policy, c *attack.AttackCommand) { c.Parameters.CustomParams = map[string]any{} },
		"custom-extra-key": func(p *Policy, c *attack.AttackCommand) {
			c.Parameters.CustomParams = map[string]any{"template": "disclose-restricted", "x": "y"}
		},
		"custom-wrong-key": func(p *Policy, c *attack.AttackCommand) {
			c.Parameters.CustomParams = map[string]any{"tmpl": "disclose-restricted"}
		},
		"template-nonstring": func(p *Policy, c *attack.AttackCommand) { c.Parameters.CustomParams = map[string]any{"template": 1} },
		"template-unknown": func(p *Policy, c *attack.AttackCommand) {
			c.Parameters.CustomParams = map[string]any{"template": "drop-tables"}
		},
	} {
		p := sqliPolicy()
		c := sqliCommand(p.Context)
		change(&p, &c)
		if _, err := p.Admit(c); err == nil {
			t.Fatalf("%s: command admitted but must be refused", name)
		}
	}
}

// The SQLi customParams acceptance must not leak to the legacy command types: a legacy command still rejects
// any customParams, including the SQLi template key.
func TestLegacyStillRejectsCustomParams(t *testing.T) {
	f := load(t)
	c := f.Command
	c.Parameters.CustomParams = map[string]any{"template": "disclose-restricted"}
	if _, err := f.Policy.Admit(c); err == nil {
		t.Fatal("legacy command accepted SQLi customParams")
	}
}

// manifestPolicyJSON extracts the `policy.json: |` literal block from a ConfigMap manifest without a YAML
// dependency, so the committed sample can be re-validated through the real Go policy path.
func manifestPolicyJSON(t *testing.T, path string) []byte {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(string(data), "\n")
	for i, line := range lines {
		if strings.TrimSpace(line) != "policy.json: |" {
			continue
		}
		keyIndent := len(line) - len(strings.TrimLeft(line, " "))
		var block []string
		indent := -1
		for _, l := range lines[i+1:] {
			if strings.TrimSpace(l) == "" {
				block = append(block, "")
				continue
			}
			li := len(l) - len(strings.TrimLeft(l, " "))
			if li <= keyIndent {
				break
			}
			if indent == -1 {
				indent = li
			}
			block = append(block, l[indent:])
		}
		return []byte(strings.Join(block, "\n"))
	}
	t.Fatalf("no policy.json block in %s", path)
	return nil
}

// The committed SQLi manifests must load through the real Go policy path (StrictJSON exact-fields + Validate),
// stay disabled, and carry a well-formed opt-in SQLi capability.
func TestSampleManifestsLoadInGo(t *testing.T) {
	for _, name := range []string{"command-guard-config.yaml", "sqli-executor-lab.yaml"} {
		raw := manifestPolicyJSON(t, "../../../infrastructure/manifests/"+name)
		var p Policy
		if err := attack.StrictJSON(raw, &p); err != nil {
			t.Fatalf("%s: StrictJSON rejected the policy: %v", name, err)
		}
		if err := p.Validate(); err != nil {
			t.Fatalf("%s: Validate rejected the policy: %v", name, err)
		}
		if p.Enabled {
			t.Fatalf("%s: sample must ship disabled", name)
		}
		if p.SQLi == nil || p.SQLi.Enabled {
			t.Fatalf("%s: SQLi capability must be present and disabled", name)
		}
	}
}

func TestSQLiPolicyValidation(t *testing.T) {
	for name, change := range map[string]func(*SQLiCapability){
		"bad-scheme":      func(s *SQLiCapability) { s.Endpoint = "https://host.local/fixture/catalog/search" },
		"endpoint-query":  func(s *SQLiCapability) { s.Endpoint = sqliEndpoint + "?x=1" },
		"maxsends-over":   func(s *SQLiCapability) { s.MaxSends = 21 },
		"maxsends-zero":   func(s *SQLiCapability) { s.MaxSends = 0 },
		"commandsec-over": func(s *SQLiCapability) { s.MaxCommandSec = 31 },
	} {
		p := sqliPolicy()
		change(p.SQLi)
		if err := p.Validate(); err == nil {
			t.Fatalf("%s: invalid SQLi policy accepted", name)
		}
	}
}
