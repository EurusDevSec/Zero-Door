package guard

// Actual subprocesses reopen the real durable ledger and dispatcher. The effect
// is a local counter only; no SQLi executor, broker, cluster or HTTP is contacted.
import (
	"context"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
)

type offlineSQLiEffect struct{ directory string }

func (e offlineSQLiEffect) Execute(_ context.Context, c attack.AttackCommand) attack.AttackResult {
	f, err := os.OpenFile(filepath.Join(e.directory, "effects.txt"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		panic(err)
	}
	if _, err = f.WriteString("offline-effect\n"); err != nil {
		panic(err)
	}
	if err = f.Close(); err != nil {
		panic(err)
	}
	return attack.AttackResult{CommandID: c.CommandID, AttackType: "SQLI", Status: "TIMEOUT"}
}

func TestZER18SQLiRestartChild(t *testing.T) {
	directory := os.Getenv("ZER18_OFFLINE_CHILD")
	if directory == "" {
		t.Skip("subprocess helper")
	}
	f := load(t)
	policy := sqliPolicy()
	command := sqliCommand(policy.Context)
	payload, err := json.Marshal(command)
	if err != nil {
		t.Fatal(err)
	}
	envelope := f.Envelope
	envelope.Payload = base64.StdEncoding.EncodeToString(payload)
	envelope = resign(envelope, f.Key)
	ledger, err := OpenLedger(directory)
	if err != nil {
		t.Fatal(err)
	}
	defer ledger.Close()
	at := time.Unix(envelope.IssuedAt+1, 0)
	if os.Getenv("ZER18_OFFLINE_CLAIM_ONLY") == "1" {
		hash := fmt.Sprintf("%x", sha256.Sum256(payload))
		if _, _, err = ledger.ClaimAt(command.CommandID, hash, at); err != nil {
			t.Fatal(err)
		}
		return
	}
	dispatcher := Dispatcher{Policy: policy, Key: f.Key, Ledger: ledger, Now: func() time.Time { return at },
		Executors: map[string]attack.Executor{"SQLI": offlineSQLiEffect{directory}}}
	result, dispatchErr := dispatcher.Handle(context.Background(), encoded(t, envelope))
	doc := map[string]any{"status": result.Status, "command_id": result.CommandID, "error": nil}
	if dispatchErr != nil {
		doc["error"] = dispatchErr.Error()
	}
	raw, _ := json.Marshal(doc)
	if err = os.WriteFile(filepath.Join(directory, "observed.json"), raw, 0600); err != nil {
		t.Fatal(err)
	}
}

func TestZER18SQLiWorkerProcessRestartAndMissingResult(t *testing.T) {
	for _, claimOnly := range []bool{false, true} {
		t.Run(fmt.Sprint("claimOnly=", claimOnly), func(t *testing.T) {
			directory := t.TempDir()
			child := func(claim bool) {
				ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
				defer cancel()
				command := exec.CommandContext(ctx, os.Args[0], "-test.run=^TestZER18SQLiRestartChild$")
				command.Env = append(os.Environ(), "ZER18_OFFLINE_CHILD="+directory, fmt.Sprintf("ZER18_OFFLINE_CLAIM_ONLY=%d", map[bool]int{true: 1, false: 0}[claim]))
				if output, err := command.CombinedOutput(); err != nil {
					t.Fatalf("%v: %s", err, output)
				}
			}
			child(claimOnly)
			child(false)
			raw, err := os.ReadFile(filepath.Join(directory, "observed.json"))
			if err != nil {
				t.Fatal(err)
			}
			var result map[string]any
			if err = json.Unmarshal(raw, &result); err != nil {
				t.Fatal(err)
			}
			effects, readErr := os.ReadFile(filepath.Join(directory, "effects.txt"))
			if claimOnly {
				if !os.IsNotExist(readErr) || result["error"] != "DUPLICATE_OUTCOME_UNKNOWN" || result["status"] == "SUCCESS" {
					t.Fatal("unknown claim repeated or promoted", result, string(effects), readErr)
				}
			} else if readErr != nil || string(effects) != "offline-effect\n" || result["status"] != "TIMEOUT" || result["error"] != nil {
				t.Fatal("restart repeated effect or lost failure", result, string(effects), readErr)
			}
		})
	}
}
