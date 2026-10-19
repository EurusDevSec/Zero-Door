// Package guard contains admission controls, not a fault implementation.
package guard

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
)

type Envelope struct {
	Version   string `json:"version"`
	KeyID     string `json:"keyId"`
	Purpose   string `json:"purpose"`
	IssuedAt  int64  `json:"issuedAt"`
	ExpiresAt int64  `json:"expiresAt"`
	Payload   string `json:"payload"`
	Signature string `json:"signature"`
}

type Key struct {
	ID      string `json:"id"`
	Secret  string `json:"secret"`
	Purpose string `json:"purpose"`
}

func LoadKey(path string) (Key, error) {
	var key Key
	data, err := os.ReadFile(path) // #nosec G304 -- Read-only path from trusted process configuration, never a request/message.
	if err != nil {
		return key, err
	}
	if err = attack.StrictJSON(data, &key); err != nil {
		return key, err
	}
	if key.ID == "" || strings.ContainsAny(key.ID, "\r\n") || len(key.Secret) < 32 || key.Purpose != "fault" {
		return key, fmt.Errorf("SIGNER_CONFIG")
	}
	return key, nil
}

func Verify(raw []byte, key Key, now time.Time) ([]byte, error) {
	envelope, payload, err := Authenticate(raw, key)
	if err == nil {
		err = envelope.Fresh(now)
	}
	if err != nil {
		return nil, err
	}
	return payload, nil
}

// Authenticate proves the signer and exact payload before any ledger lookup.
// Freshness is checked separately for new admissions; a replay never executes.
func Authenticate(raw []byte, key Key) (Envelope, []byte, error) {
	var envelope Envelope
	if err := attack.StrictJSON(raw, &envelope); err != nil {
		return envelope, nil, fmt.Errorf("ENVELOPE_SCHEMA")
	}
	if len(key.Secret) < 32 || envelope.Version != "zd-command/1" || envelope.KeyID != key.ID ||
		key.Purpose != "fault" || envelope.Purpose != key.Purpose || envelope.IssuedAt <= 0 ||
		envelope.ExpiresAt <= envelope.IssuedAt || envelope.ExpiresAt-envelope.IssuedAt > 60 {
		return envelope, nil, fmt.Errorf("AUTH_CONTEXT_OR_EXPIRY")
	}
	signed := fmt.Sprintf("%s\n%s\n%s\n%d\n%d\n%s", envelope.Version, envelope.KeyID, envelope.Purpose, envelope.IssuedAt, envelope.ExpiresAt, envelope.Payload)
	mac := hmac.New(sha256.New, []byte(key.Secret))
	mac.Write([]byte(signed))
	signature, err := hex.DecodeString(envelope.Signature)
	if err != nil || !hmac.Equal(signature, mac.Sum(nil)) {
		return envelope, nil, fmt.Errorf("AUTH_SIGNATURE")
	}
	payload, err := base64.StdEncoding.Strict().DecodeString(envelope.Payload)
	if err != nil || len(payload) > 16384 {
		return envelope, nil, fmt.Errorf("AUTH_PAYLOAD")
	}
	return envelope, payload, nil
}

func (e Envelope) Fresh(now time.Time) error {
	// Permit at most two seconds of signer clock lead, never extend expiry.
	if e.IssuedAt > now.Unix()+2 || e.ExpiresAt <= now.Unix() {
		return fmt.Errorf("AUTH_CONTEXT_OR_EXPIRY")
	}
	return nil
}
