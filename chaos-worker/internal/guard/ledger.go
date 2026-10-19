package guard

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
)

type entry struct {
	AcceptedAt int64                `json:"acceptedAt"`
	ID         string               `json:"id"`
	Hash       string               `json:"hash"`
	Result     *attack.AttackResult `json:"result"`
}

// Ledger is single-owner, append+fsync before dispatch. Claims are never expired automatically.
// An abandoned lock or ambiguous claim requires operator reconciliation, not a retry of effects.
type Ledger struct {
	mu      sync.Mutex
	file    *os.File
	lock    string
	entries map[string]entry
	failed  error
}

func OpenLedger(directory string) (*Ledger, error) {
	if directory == "" {
		return nil, fmt.Errorf("LEDGER_REQUIRED")
	}
	if err := os.MkdirAll(directory, 0700); err != nil {
		return nil, err
	}
	info, err := os.Lstat(directory)
	if err != nil || !info.IsDir() || info.Mode()&os.ModeSymlink != 0 {
		return nil, fmt.Errorf("LEDGER_DIRECTORY")
	}
	lock := filepath.Join(directory, "owner.lock")
	owner, err := os.OpenFile(lock, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600) // #nosec G304 -- Fixed basename under the configured private ledger; O_EXCL enforces one owner.
	if err != nil {
		return nil, fmt.Errorf("LEDGER_OWNER: %w", err)
	}
	if err = owner.Close(); err != nil {
		return nil, err
	}
	ok := false
	defer func() {
		if !ok {
			_ = os.Remove(lock)
		}
	}()
	path := filepath.Join(directory, "claims.jsonl")
	if stat, e := os.Lstat(path); e == nil && !stat.Mode().IsRegular() {
		return nil, fmt.Errorf("LEDGER_FILE")
	} else if e != nil && !os.IsNotExist(e) {
		return nil, e
	}
	f, err := os.OpenFile(path, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0600) // #nosec G304 -- Fixed basename, private configured directory, regular-file check and exclusive owner lock above.
	if err != nil {
		return nil, err
	}
	l := &Ledger{file: f, lock: lock, entries: map[string]entry{}}
	valid := false
	defer func() {
		if !valid {
			_ = f.Close()
		}
	}()
	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 4096), 65536)
	for scanner.Scan() {
		data := append([]byte(nil), scanner.Bytes()...)
		var e entry
		if attack.StrictJSON(data, &e) != nil || !uuidID.MatchString(e.ID) || len(e.Hash) != 64 || e.AcceptedAt <= 0 {
			return nil, fmt.Errorf("LEDGER_INTEGRITY")
		}
		previous, exists := l.entries[e.ID]
		if (exists && (previous.Hash != e.Hash || previous.AcceptedAt != e.AcceptedAt || previous.Result != nil || e.Result == nil)) || (!exists && e.Result != nil) {
			return nil, fmt.Errorf("LEDGER_SEQUENCE")
		}
		l.entries[e.ID] = e
	}
	if err = scanner.Err(); err != nil {
		return nil, err
	}
	// Scanner accepts a final unterminated JSON line; the writer never creates one.
	size, err := f.Seek(0, 2)
	if err != nil {
		return nil, err
	}
	if size > 0 {
		var last [1]byte
		if _, err = f.ReadAt(last[:], size-1); err != nil || last[0] != '\n' {
			return nil, fmt.Errorf("LEDGER_TRUNCATED")
		}
	}
	if len(l.entries) > 10000 {
		return nil, fmt.Errorf("LEDGER_CAPACITY")
	}
	valid = true
	ok = true
	return l, nil
}
func (l *Ledger) append(e entry) error {
	if l.failed != nil {
		return l.failed
	}
	raw, err := json.Marshal(e)
	if err == nil {
		raw = append(raw, '\n')
		var n int
		n, err = l.file.Write(raw)
		if err == nil && n != len(raw) {
			err = fmt.Errorf("SHORT_WRITE")
		}
	}
	if err == nil {
		err = l.file.Sync()
	}
	if err != nil {
		l.failed = fmt.Errorf("LEDGER_FAILED: %w", err)
		return l.failed
	}
	l.entries[e.ID] = e
	return nil
}
func (l *Ledger) Claim(id, hash string) (bool, *attack.AttackResult, error) {
	return l.ClaimAt(id, hash, time.Now())
}

// Lookup is read-only: it cannot create a claim or authorize a new effect.
func (l *Ledger) Lookup(id, hash string) (bool, *attack.AttackResult, error) {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.failed != nil {
		return false, nil, l.failed
	}
	old, exists := l.entries[id]
	if exists && old.Hash != hash {
		return true, nil, fmt.Errorf("ID_CONFLICT")
	}
	return exists, old.Result, nil
}

func (l *Ledger) ClaimAt(id, hash string, now time.Time) (bool, *attack.AttackResult, error) {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.failed != nil {
		return false, nil, l.failed
	}
	if old, ok := l.entries[id]; ok {
		if old.Hash != hash {
			return false, nil, fmt.Errorf("ID_CONFLICT")
		}
		return false, old.Result, nil
	}
	if len(l.entries) >= 10000 {
		return false, nil, fmt.Errorf("LEDGER_FULL")
	}
	for _, old := range l.entries {
		if old.Result == nil {
			return false, nil, fmt.Errorf("ACTIVE_OR_UNKNOWN_COMMAND")
		}
		if now.Unix() < old.AcceptedAt+6 {
			return false, nil, fmt.Errorf("COMMAND_RATE")
		}
	}
	return true, nil, l.append(entry{ID: id, Hash: hash, AcceptedAt: now.Unix()})
}
func (l *Ledger) Complete(id string, result attack.AttackResult) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	e, ok := l.entries[id]
	if !ok || e.Result != nil {
		return fmt.Errorf("LEDGER_COMPLETION")
	}
	e.Result = &result
	return l.append(e)
}
func (l *Ledger) Close() error {
	l.mu.Lock()
	defer l.mu.Unlock()
	if err := l.file.Close(); err != nil {
		return err
	}
	return os.Remove(l.lock)
}

func (l *Ledger) Failure() error { l.mu.Lock(); defer l.mu.Unlock(); return l.failed }
