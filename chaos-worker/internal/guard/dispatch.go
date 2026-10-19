package guard

import (
	"context"
	"crypto/sha256"
	"fmt"
	"sync"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
	"github.com/google/uuid"
)

// Dispatcher serializes admission and execution: one active command and one shared budget.
// No unbounded goroutine or per-message budget expansion. Multiple worker replicas are unsupported.
type Dispatcher struct {
	mu        sync.Mutex
	Policy    Policy
	Key       Key
	Ledger    *Ledger
	Executors map[string]attack.Executor
	Now       func() time.Time
}

func (d *Dispatcher) Handle(ctx context.Context, raw []byte) (attack.AttackResult, error) {
	d.mu.Lock()
	defer d.mu.Unlock()
	result := attack.AttackResult{ResultID: uuid.NewString(), Timestamp: attack.NowISO(), Source: "chaos-worker", Status: "REJECTED"}
	reject := func(err error) (attack.AttackResult, error) {
		result.Details.ErrorMessage = err.Error()
		return result, err
	}
	now := time.Now()
	if d.Now != nil {
		now = d.Now()
	}
	envelope, payload, err := Authenticate(raw, d.Key)
	if err != nil {
		return reject(err)
	}
	cmd, err := attack.ParseCommand(payload)
	if err != nil {
		return reject(fmt.Errorf("COMMAND_SCHEMA"))
	}
	result.CommandID = cmd.CommandID
	result.AttackType = cmd.AttackType
	hash := fmt.Sprintf("%x", sha256.Sum256(payload))
	if d.Ledger == nil {
		return reject(fmt.Errorf("DISPATCH_CONFIG"))
	}
	exists, previous, err := d.Ledger.Lookup(cmd.CommandID, hash)
	if err != nil {
		return reject(err)
	}
	if exists {
		if previous != nil {
			return *previous, nil
		}
		return reject(fmt.Errorf("DUPLICATE_OUTCOME_UNKNOWN"))
	}
	if err = envelope.Fresh(now); err != nil {
		return reject(err)
	}
	if ctx.Err() != nil {
		return reject(ctx.Err())
	}
	cmd, err = d.Policy.Admit(cmd)
	if err != nil {
		return reject(err)
	}
	if !d.Policy.Enabled {
		return reject(fmt.Errorf("EXECUTOR_DISABLED"))
	}
	executor := d.Executors[cmd.AttackType]
	if executor == nil || d.Ledger == nil {
		return reject(fmt.Errorf("DISPATCH_CONFIG"))
	}
	fresh, previous, err := d.Ledger.ClaimAt(cmd.CommandID, hash, now)
	if err != nil {
		return reject(err)
	}
	if !fresh {
		if previous != nil {
			return *previous, nil
		}
		return reject(fmt.Errorf("DUPLICATE_OUTCOME_UNKNOWN"))
	}
	if ctx.Err() != nil {
		return reject(ctx.Err())
	} // Keep ambiguous claim, never replay an uncertain effect.
	bounded, cancel := context.WithTimeout(ctx, attack.EffectiveDuration(cmd, d.Policy.MaxDurationSec))
	defer cancel()
	result = executor.Execute(bounded, cmd)
	if err = d.Ledger.Complete(cmd.CommandID, result); err != nil {
		return result, err
	}
	return result, nil
}
