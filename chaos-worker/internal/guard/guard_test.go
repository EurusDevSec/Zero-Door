package guard

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
)

type fixture struct {
	Policy   Policy
	Command  attack.AttackCommand
	Key      Key
	Envelope Envelope
}

func load(t *testing.T) fixture {
	t.Helper()
	raw, err := os.ReadFile("../../../tests/fixtures/zer12/command-guards.json")
	if err != nil {
		t.Fatal(err)
	}
	var f fixture
	if err = json.Unmarshal(raw, &f); err != nil {
		t.Fatal(err)
	}
	return f
}
func encoded(t *testing.T, e Envelope) []byte {
	t.Helper()
	data, err := json.Marshal(e)
	if err != nil {
		t.Fatal(err)
	}
	return data
}
func TestSharedSignatureAndAuth(t *testing.T) {
	f := load(t)
	now := time.Unix(1700000001, 0)
	data, err := Verify(encoded(t, f.Envelope), f.Key, now)
	if err != nil {
		t.Fatal(err)
	}
	cmd, err := attack.ParseCommand(data)
	if err != nil || cmd.CommandID != f.Command.CommandID {
		t.Fatal(cmd, err)
	}
	for _, change := range []func(*Envelope){func(e *Envelope) { e.Payload += "A" }, func(e *Envelope) { e.Purpose = "heal" }, func(e *Envelope) { e.KeyID = "operator" }, func(e *Envelope) { e.ExpiresAt += 1 }, func(e *Envelope) { e.Signature = strings.Repeat("0", 64) }, func(e *Envelope) { e.Version = "unknown" }} {
		e := f.Envelope
		change(&e)
		if _, err := Verify(encoded(t, e), f.Key, now); err == nil {
			t.Fatal("forgery accepted")
		}
	}
	for _, at := range []int64{1699999997, 1700000060, 1700000090} {
		if _, err := Verify(encoded(t, f.Envelope), f.Key, time.Unix(at, 0)); err == nil {
			t.Fatal("expiry accepted", at)
		}
	}
}
func TestPolicyCapsAndTargets(t *testing.T) {
	f := load(t)
	bounded, err := f.Policy.Admit(f.Command)
	if err != nil {
		t.Fatal(err)
	}
	if bounded.Parameters.DurationSec != 1 || bounded.Parameters.Concurrency != 2 {
		t.Fatal("operator cap bypass", bounded)
	}
	for _, change := range []func(*attack.AttackCommand){
		func(c *attack.AttackCommand) { c.Context.Group = "B2" }, func(c *attack.AttackCommand) { c.Context.TrialID = "trl_" + strings.Repeat("3", 32) },
		func(c *attack.AttackCommand) { c.CommandID = "short" }, func(c *attack.AttackCommand) { c.Target.Namespace = "monitoring" }, func(c *attack.AttackCommand) { c.Target.Service = "frontend,app" },
		func(c *attack.AttackCommand) { c.Parameters.DurationSec = -1 }, func(c *attack.AttackCommand) { c.Parameters.Concurrency = 0 }, func(c *attack.AttackCommand) { c.Parameters.CustomParams = map[string]any{"labelSelector": ""} },
		func(c *attack.AttackCommand) { c.SafetyLimits.AllowedNamespaces = []string{"target-app", "monitoring"} },
	} {
		c := f.Command
		change(&c)
		if _, err := f.Policy.Admit(c); err == nil {
			t.Fatal("bad command admitted", c)
		}
	}
	for _, group := range []string{"B0", "BM", "B1", "B2", "B3"} {
		p := f.Policy
		c := f.Command
		p.Context.Group = group
		c.Context = p.Context
		if _, err := p.Admit(c); err != nil {
			t.Fatal("harness fault incorrectly treated as heal", group, err)
		}
	}
}
func TestLedgerOwnershipRestartConflictAndUnknown(t *testing.T) {
	dir := t.TempDir()
	l, err := OpenLedger(dir)
	if err != nil {
		t.Fatal(err)
	}
	if other, err := OpenLedger(dir); err == nil {
		other.Close()
		t.Fatal("second writer")
	}
	id := "11111111-1111-4111-8111-111111111111"
	hash := strings.Repeat("a", 64)
	fresh, _, err := l.Claim(id, hash)
	if !fresh || err != nil {
		t.Fatal(fresh, err)
	}
	if err = l.Close(); err != nil {
		t.Fatal(err)
	}
	l, err = OpenLedger(dir)
	if err != nil {
		t.Fatal(err)
	}
	defer l.Close()
	fresh, old, err := l.Claim(id, hash)
	if fresh || old != nil || err != nil {
		t.Fatal("unknown must not replay")
	}
	if _, _, err = l.Claim(id, strings.Repeat("b", 64)); err == nil {
		t.Fatal("conflict accepted")
	}
	result := attack.AttackResult{Status: "FAILED", CommandID: id}
	if err = l.Complete(id, result); err != nil {
		t.Fatal(err)
	}
	fresh, old, err = l.Claim(id, hash)
	if fresh || old == nil || old.Status != "FAILED" || err != nil {
		t.Fatal("completed result not reusable", old, err)
	}
}
func TestLedgerConcurrentClaimAndIOFailure(t *testing.T) {
	l, err := OpenLedger(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	defer l.Close()
	var claims int32
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			fresh, _, e := l.Claim("11111111-1111-4111-8111-111111111111", strings.Repeat("a", 64))
			if e != nil {
				t.Error(e)
			}
			if fresh {
				atomic.AddInt32(&claims, 1)
			}
		}()
	}
	wg.Wait()
	if claims != 1 {
		t.Fatal(claims)
	}
	if err = l.Complete("11111111-1111-4111-8111-111111111111", attack.AttackResult{Status: "FAILED"}); err != nil {
		t.Fatal(err)
	}
	l.file.Close()
	if _, _, err = l.ClaimAt("22222222-2222-4222-8222-222222222222", strings.Repeat("b", 64), time.Now().Add(6*time.Second)); err == nil {
		t.Fatal("write failure not visible")
	}
	if _, _, err = l.Claim("11111111-1111-4111-8111-111111111111", strings.Repeat("a", 64)); err == nil {
		t.Fatal("failure not sticky")
	}
}
func TestLedgerCorruptionAndAbandonedOwner(t *testing.T) {
	for _, raw := range []string{"garbage\n", `{"id":"11111111-1111-4111-8111-111111111111","hash":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","result":null}`} {
		dir := t.TempDir()
		if err := os.WriteFile(filepath.Join(dir, "claims.jsonl"), []byte(raw), 0600); err != nil {
			t.Fatal(err)
		}
		if l, err := OpenLedger(dir); err == nil {
			l.Close()
			t.Fatal("corrupt accepted")
		}
	}
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "owner.lock"), nil, 0600)
	if l, err := OpenLedger(dir); err == nil {
		l.Close()
		t.Fatal("abandoned owner bypass")
	}
}

type fakeExecutor struct{ calls int32 }

func (e *fakeExecutor) Execute(ctx context.Context, c attack.AttackCommand) attack.AttackResult {
	atomic.AddInt32(&e.calls, 1)
	return attack.AttackResult{CommandID: c.CommandID, Status: "SUCCESS"}
}
func TestDispatchRealAdmissionNoSideEffectsAndReplay(t *testing.T) {
	f := load(t)
	l, err := OpenLedger(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	defer l.Close()
	ex := &fakeExecutor{}
	d := Dispatcher{Policy: f.Policy, Key: f.Key, Ledger: l, Now: func() time.Time { return time.Unix(1700000001, 0) }, Executors: map[string]attack.Executor{"HTTP_FLOOD": ex}}
	raw := encoded(t, f.Envelope)
	d.Policy.Enabled = false
	if _, err = d.Handle(context.Background(), raw); err == nil {
		t.Fatal("disabled")
	}
	if ex.calls != 0 {
		t.Fatal("disabled effect")
	}
	d.Policy.Enabled = true
	bad := f.Envelope
	bad.Purpose = "heal"
	if _, err = d.Handle(context.Background(), encoded(t, bad)); err == nil {
		t.Fatal("wrong role")
	}
	cancelled, cancel := context.WithCancel(context.Background())
	cancel()
	d.Handle(cancelled, raw)
	if ex.calls != 0 {
		t.Fatal("cancelled effect")
	}
	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			r, e := d.Handle(context.Background(), raw)
			if e != nil || r.Status != "SUCCESS" {
				t.Error(r, e)
			}
		}()
	}
	wg.Wait()
	if ex.calls != 1 {
		t.Fatal("duplicate effect", ex.calls)
	}
	// A new dispatcher with the same durable ledger does not execute again.
	d2 := Dispatcher{Policy: d.Policy, Key: d.Key, Ledger: l, Now: d.Now, Executors: d.Executors}
	d2.Handle(context.Background(), raw)
	if ex.calls != 1 {
		t.Fatal("restart replay")
	}
}

func TestAdmissionPacingAndUnknownSurviveRestart(t *testing.T) {
	dir := t.TempDir()
	l, err := OpenLedger(dir)
	if err != nil {
		t.Fatal(err)
	}
	first, second := "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"
	hash := strings.Repeat("a", 64)
	at := time.Unix(1700000000, 0)
	if _, _, err = l.ClaimAt(first, hash, at); err != nil {
		t.Fatal(err)
	}
	if _, _, err = l.ClaimAt(second, hash, at.Add(7*time.Second)); err == nil || err.Error() != "ACTIVE_OR_UNKNOWN_COMMAND" {
		t.Fatal("unknown overlap", err)
	}
	if err = l.Complete(first, attack.AttackResult{Status: "FAILED"}); err != nil {
		t.Fatal(err)
	}
	l.Close()
	l, err = OpenLedger(dir)
	if err != nil {
		t.Fatal(err)
	}
	defer l.Close()
	if _, _, err = l.ClaimAt(second, hash, at.Add(5*time.Second)); err == nil || err.Error() != "COMMAND_RATE" {
		t.Fatal("restart pacing", err)
	}
	if fresh, _, err := l.ClaimAt(second, hash, at.Add(6*time.Second)); !fresh || err != nil {
		t.Fatal("valid paced control", fresh, err)
	}
}
