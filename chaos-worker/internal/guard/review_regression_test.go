package guard

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
)

func resign(e Envelope, key Key) Envelope {
	mac := hmac.New(sha256.New, []byte(key.Secret))
	mac.Write([]byte(fmt.Sprintf("%s\n%s\n%s\n%d\n%d\n%s", e.Version, e.KeyID, e.Purpose, e.IssuedAt, e.ExpiresAt, e.Payload)))
	e.Signature = hex.EncodeToString(mac.Sum(nil))
	return e
}

func TestReviewExactJSONTagsAtEveryBoundary(t *testing.T) {
	f := load(t)
	policy, _ := json.Marshal(f.Policy)
	for _, raw := range []string{
		strings.Replace(string(policy), `"enabled":true`, `"enabled":false,"Enabled":true`, 1),
		strings.Replace(string(policy), `"enabled":true`, `"Enabled":true`, 1),
		strings.Replace(string(policy), `"run_id"`, `"Run_ID"`, 1),
		strings.Replace(string(policy), `"namespace"`, `"Namespace"`, 1),
	} {
		var p Policy
		if err := attack.StrictJSON([]byte(raw), &p); err == nil {
			t.Fatalf("alias accepted: %s", raw)
		}
	}
	payload, _ := base64.StdEncoding.DecodeString(f.Envelope.Payload)
	bad := strings.Replace(string(payload), `"source":"nemesis"`, `"source":"blocked","Source":"nemesis"`, 1)
	if _, err := attack.ParseCommand([]byte(bad)); err == nil {
		t.Fatal("case-fold command accepted")
	}
	var p Policy
	if err := attack.StrictJSON(policy, &p); err != nil {
		t.Fatal("valid control", err)
	}
}

func TestReviewClockLeadBoundAndExpiry(t *testing.T) {
	f := load(t)
	for _, lead := range []int64{0, 1, 2} {
		if _, err := Verify(encoded(t, f.Envelope), f.Key, time.Unix(f.Envelope.IssuedAt-lead, 0)); err != nil {
			t.Fatal("bounded clock lead", lead, err)
		}
	}
	for _, at := range []int64{f.Envelope.IssuedAt - 3, f.Envelope.ExpiresAt, f.Envelope.ExpiresAt + 1} {
		if _, err := Verify(encoded(t, f.Envelope), f.Key, time.Unix(at, 0)); err == nil {
			t.Fatal("invalid time accepted", at)
		}
	}
}

func TestReviewExpiredRedeliveryKeepsOutcomeWithoutEffect(t *testing.T) {
	f := load(t)
	directory := t.TempDir()
	l, err := OpenLedger(directory)
	if err != nil {
		t.Fatal(err)
	}
	ex := &fakeExecutor{}
	at := time.Unix(f.Envelope.IssuedAt+1, 0)
	d := Dispatcher{Policy: f.Policy, Key: f.Key, Ledger: l, Now: func() time.Time { return at }, Executors: map[string]attack.Executor{"HTTP_FLOOD": ex}}
	raw := encoded(t, f.Envelope)
	first, err := d.Handle(context.Background(), raw)
	if err != nil {
		t.Fatal(err)
	}
	if err = l.Close(); err != nil {
		t.Fatal(err)
	}
	l, err = OpenLedger(directory)
	if err != nil {
		t.Fatal(err)
	}
	defer l.Close()
	d.Ledger = l
	at = time.Unix(f.Envelope.ExpiresAt+3600, 0)
	d.Policy.Enabled = false // Result retrieval is not a new operational admission.
	again, err := d.Handle(context.Background(), raw)
	if err != nil || again != first || ex.calls != 1 {
		t.Fatal("lost completed receipt", again, err, ex.calls)
	}
	forged := f.Envelope
	forged.Signature = strings.Repeat("0", 64)
	if _, err = d.Handle(context.Background(), encoded(t, forged)); err == nil {
		t.Fatal("ledger bypassed MAC")
	}
	changed := f.Command
	changed.Parameters.DurationSec++
	payload, _ := json.Marshal(changed)
	conflict := f.Envelope
	conflict.Payload = base64.StdEncoding.EncodeToString(payload)
	conflict = resign(conflict, f.Key)
	r, err := d.Handle(context.Background(), encoded(t, conflict))
	if err == nil || err.Error() != "ID_CONFLICT" || r.CommandID != f.Command.CommandID {
		t.Fatal(r, err)
	}
	changed.CommandID = "22222222-2222-4222-8222-222222222222"
	payload, _ = json.Marshal(changed)
	fresh := f.Envelope
	fresh.Payload = base64.StdEncoding.EncodeToString(payload)
	fresh = resign(fresh, f.Key)
	d.Policy.Enabled = true
	if _, err = d.Handle(context.Background(), encoded(t, fresh)); err == nil {
		t.Fatal("expired fresh effect")
	}
	if ex.calls != 1 {
		t.Fatal("redelivery executed", ex.calls)
	}
}

func TestReviewExpiredPendingIsStillUnknown(t *testing.T) {
	f := load(t)
	l, err := OpenLedger(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	defer l.Close()
	payload, _ := base64.StdEncoding.DecodeString(f.Envelope.Payload)
	hash := fmt.Sprintf("%x", sha256.Sum256(payload))
	if _, _, err = l.ClaimAt(f.Command.CommandID, hash, time.Unix(f.Envelope.IssuedAt, 0)); err != nil {
		t.Fatal(err)
	}
	ex := &fakeExecutor{}
	d := Dispatcher{Policy: f.Policy, Key: f.Key, Ledger: l, Now: func() time.Time { return time.Unix(f.Envelope.ExpiresAt+1, 0) }, Executors: map[string]attack.Executor{"HTTP_FLOOD": ex}}
	r, err := d.Handle(context.Background(), encoded(t, f.Envelope))
	if err == nil || err.Error() != "DUPLICATE_OUTCOME_UNKNOWN" || r.CommandID != f.Command.CommandID || ex.calls != 0 {
		t.Fatal(r, err, ex.calls)
	}
}
