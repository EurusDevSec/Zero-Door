package attack

import (
	"context"
	"encoding/json"
	"io"
	"net"
	"net/http"
	"os"
	"strings"
	"sync"
	"testing"
	"time"
)

// privateResolver is the default offline resolver for executor tests: the endpoint host resolves to a private
// cluster address, so the peer preflight passes. Peer-rejection tests inject their own resolver instead.
func privateResolver(context.Context, string) ([]net.IP, error) {
	return []net.IP{net.IPv4(10, 1, 2, 3)}, nil
}

type delayedBody struct {
	read bool
}

func (b *delayedBody) Read(p []byte) (int, error) {
	if b.read {
		return 0, io.EOF
	}
	b.read = true
	time.Sleep(120 * time.Millisecond)
	return copy(p, []byte(`{"results":[{"sku":"RES-APP-900","visibility":"restricted"}],"count":1}`)), io.EOF
}
func (*delayedBody) Close() error { return nil }

// The CI bridge serializes the real Go AttackResult, then the Python test feeds it
// through evaluator, locked contract and scorer semantic validation.
func TestSQLiActualResultBridge(t *testing.T) {
	path := os.Getenv("ZD_SQLI_RESULT_PATH")
	ft := &fakeTransport{handle: func(int, *http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: 200, Header: make(http.Header), Body: &delayedBody{}}, nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5,
		Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	started := time.Now()
	result := e.Execute(context.Background(), sqliCmd("disclose-restricted"))
	send := result.Details.SQLi.Sends[0]
	observed, err := time.Parse("2006-01-02T15:04:05.000Z", send.ObservedAt)
	if err != nil || observed.Before(started.Add(100*time.Millisecond)) {
		t.Fatalf("observedAt precedes body completion: %q %v", send.ObservedAt, err)
	}
	if path != "" {
		raw, err := json.Marshal(result)
		if err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, raw, 0o600); err != nil {
			t.Fatal(err)
		}
	}
}

// fakeTransport counts every RoundTrip (so a test can prove exactly how many sends happened) and lets the test
// shape each response. It returns the context error when the context is already cancelled, like a real client.
type fakeTransport struct {
	mu     sync.Mutex
	calls  int
	handle func(n int, req *http.Request) (*http.Response, error)
}

func (f *fakeTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	f.mu.Lock()
	f.calls++
	n := f.calls
	f.mu.Unlock()
	if err := req.Context().Err(); err != nil {
		return nil, err
	}
	return f.handle(n, req)
}

func (f *fakeTransport) count() int {
	f.mu.Lock()
	defer f.mu.Unlock()
	return f.calls
}

func jsonResp(status int, body string) *http.Response {
	return &http.Response{StatusCode: status, Body: io.NopCloser(strings.NewReader(body)), Header: make(http.Header)}
}

const sqliTestURL = "http://zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000/fixture/catalog/search"

func sqliCmd(templateID string) AttackCommand {
	return AttackCommand{
		CommandID: "11111111-1111-4111-8111-111111111111", Source: "nemesis", AttackType: "SQLI",
		Target: AttackTarget{Namespace: SQLiNamespace, Service: SQLiService, URL: sqliTestURL},
		Parameters: AttackParameters{DurationSec: 30, Intensity: "LOW", Concurrency: 1,
			CustomParams: map[string]any{"template": templateID}},
		SafetyLimits: SafetyLimits{MaxDurationSec: 30, AllowedNamespaces: []string{SQLiNamespace}},
	}
}

func TestSQLiExecutorDisclosureRecordsRestricted(t *testing.T) {
	body := `{"results":[{"sku":"PUB-APP-001","visibility":"public"},{"sku":"RES-APP-900","visibility":"restricted"},{"sku":"RES-INT-001","visibility":"restricted"},{"sku":"RES-INT-002","visibility":"restricted"}],"count":4}`
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		if got := r.URL.Query().Get("category"); got != "zzz' OR visibility='restricted' --" {
			t.Errorf("category not sent verbatim: %q", got)
		}
		if r.Method != http.MethodGet {
			t.Errorf("method %q", r.Method)
		}
		return jsonResp(200, body), nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("disclose-restricted"))
	if res.Status != "SUCCESS" {
		t.Fatalf("status %s %s", res.Status, res.Details.ErrorMessage)
	}
	if res.Details.SQLi == nil || len(res.Details.SQLi.Sends) != 1 {
		t.Fatal("missing observation")
	}
	s := res.Details.SQLi.Sends[0]
	if s.Status != 200 || s.RestrictedRows != 3 || len(s.RestrictedSKUs) != 3 {
		t.Fatalf("restricted evidence not recorded: %+v", s)
	}
	if ft.count() != 1 {
		t.Fatalf("sends = %d, want 1", ft.count())
	}
}

func TestSQLiExecutorBenignHasNoRestricted(t *testing.T) {
	body := `{"results":[{"sku":"PUB-APP-001","visibility":"public"},{"sku":"PUB-APP-002","visibility":"public"}],"count":2}`
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) { return jsonResp(200, body), nil }}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("benign-apparel"))
	if res.Status != "SUCCESS" || res.Details.SQLi.Sends[0].RestrictedRows != 0 || res.Details.SQLi.Sends[0].Rows != 2 {
		t.Fatalf("benign observation wrong: %+v", res.Details.SQLi.Sends[0])
	}
}

func TestSQLiExecutorRespectsSendCap(t *testing.T) {
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		return jsonResp(200, `{"results":[],"count":0}`), nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 5, MaxCommandSec: 30, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("benign-home"))
	if res.Details.RequestsSent != 5 || ft.count() != 5 {
		t.Fatalf("send cap broken: requestsSent=%d calls=%d", res.Details.RequestsSent, ft.count())
	}
}

func TestSQLiExecutorCancelledBeforeStart(t *testing.T) {
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		return jsonResp(200, `{"results":[],"count":0}`), nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 5, MaxCommandSec: 30, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	res := e.Execute(ctx, sqliCmd("benign-home"))
	if ft.count() != 0 || res.Details.RequestsSent != 0 || res.Status != "TIMEOUT" {
		t.Fatalf("cancel-before start sent: calls=%d sends=%d status=%s", ft.count(), res.Details.RequestsSent, res.Status)
	}
}

func TestSQLiExecutorStopsCreatingSendsOnCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	ft := &fakeTransport{}
	ft.handle = func(n int, r *http.Request) (*http.Response, error) {
		if n >= 3 {
			cancel() // cancel while the 3rd send is in flight (SIGTERM-like)
		}
		return jsonResp(200, `{"results":[],"count":0}`), nil
	}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 20, MaxCommandSec: 30, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(ctx, sqliCmd("benign-home"))
	if ft.count() > 4 {
		t.Fatalf("kept sending after cancel: %d", ft.count())
	}
	if res.Status != "TIMEOUT" {
		t.Fatalf("status %s", res.Status)
	}
}

func TestSQLiExecutorBoundsResponse(t *testing.T) {
	big := `{"results":[` + strings.Repeat(`{"sku":"X","visibility":"public"},`, 20000) + `{"sku":"Y","visibility":"public"}],"count":1}`
	if len(big) <= SQLiMaxResponse {
		t.Fatalf("test body not over cap: %d", len(big))
	}
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) { return jsonResp(200, big), nil }}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("benign-home"))
	if res.Details.SQLi.Sends[0].Error != "RESPONSE_TOO_LARGE" {
		t.Fatalf("response not bounded: %+v", res.Details.SQLi.Sends[0])
	}
}

func TestSQLiExecutorDoesNotFollowRedirect(t *testing.T) {
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		resp := jsonResp(302, "")
		resp.Header.Set("Location", "http://elsewhere.example/")
		return resp, nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("benign-home"))
	if ft.count() != 1 {
		t.Fatalf("redirect followed: %d calls", ft.count())
	}
	if res.Details.SQLi.Sends[0].Status != 302 {
		t.Fatalf("status %d", res.Details.SQLi.Sends[0].Status)
	}
}

func TestSQLiExecutorNoImplicitRetry(t *testing.T) {
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) { return nil, io.ErrUnexpectedEOF }}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("benign-home"))
	if ft.count() != 1 {
		t.Fatalf("implicit retry: %d calls", ft.count())
	}
	if res.Details.SQLi.Sends[0].Error != "TRANSPORT" {
		t.Fatalf("error %q", res.Details.SQLi.Sends[0].Error)
	}
	if res.Status != "FAILED" {
		t.Fatalf("all-errored command should be FAILED, got %s", res.Status)
	}
}

func TestSQLiExecutorGuardRejectionsSendNothing(t *testing.T) {
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		t.Error("guard rejection must not send")
		return jsonResp(200, "{}"), nil
	}}
	for name, mut := range map[string]func(*SQLIExecutor, *AttackCommand){
		"bad-endpoint": func(e *SQLIExecutor, c *AttackCommand) { c.Target.URL = "http://host.local/fixture/orders" },
		"unknown-template": func(e *SQLIExecutor, c *AttackCommand) {
			c.Parameters.CustomParams = map[string]any{"template": "nope"}
		},
		"two-custom": func(e *SQLIExecutor, c *AttackCommand) {
			c.Parameters.CustomParams = map[string]any{"template": "benign-home", "x": 1}
		},
		"concurrency":   func(e *SQLIExecutor, c *AttackCommand) { c.Parameters.Concurrency = 2 },
		"maxsends-zero": func(e *SQLIExecutor, c *AttackCommand) { e.MaxSends = 0 },
		"maxsends-over": func(e *SQLIExecutor, c *AttackCommand) { e.MaxSends = SQLiMaxSends + 1 },
		"budget-zero":   func(e *SQLIExecutor, c *AttackCommand) { e.MaxCommandSec = 0 },
		"budget-over":   func(e *SQLIExecutor, c *AttackCommand) { e.MaxCommandSec = SQLiPerCommandSec + 1 },
	} {
		e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
		c := sqliCmd("benign-home")
		mut(e, &c)
		res := e.Execute(context.Background(), c)
		if res.Status != "REJECTED" {
			t.Fatalf("%s: status %s, want REJECTED", name, res.Status)
		}
	}
	if ft.count() != 0 {
		t.Fatalf("guard sent %d requests", ft.count())
	}
}

func TestSQLiExecutorDefaultPaceIsOnePerSecond(t *testing.T) {
	if testing.Short() {
		t.Skip("timing test")
	}
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		return jsonResp(200, `{"results":[],"count":0}`), nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 2, MaxCommandSec: 5, Transport: ft, Resolver: privateResolver} // pace 0 => default one send per second
	start := time.Now()
	res := e.Execute(context.Background(), sqliCmd("benign-home"))
	if res.Details.RequestsSent != 2 {
		t.Fatalf("sends %d", res.Details.RequestsSent)
	}
	if elapsed := time.Since(start); elapsed < 900*time.Millisecond {
		t.Fatalf("second send too fast: %v (not paced at 1 rps)", elapsed)
	}
}

// ZR42-02: an HTTP 200 whose body is not a well-formed catalog result is a SCHEMA error, never a clean
// "no restricted rows" observation (so it can never be mistaken for a confident no-effect downstream).
func TestSQLiExecutorRejectsMalformed200(t *testing.T) {
	for name, body := range map[string]string{
		"empty-object":   `{}`,
		"json-null":      `null`,
		"results-null":   `{"results":null,"count":0}`,
		"missing-vis":    `{"results":[{"sku":"X"}],"count":1}`,
		"missing-sku":    `{"results":[{"visibility":"public"}],"count":1}`,
		"negative-count": `{"results":[],"count":-1}`,
		"count-mismatch": `{"results":[{"sku":"X","visibility":"public"}],"count":2}`,
		"bad-visibility": `{"results":[{"sku":"X","visibility":"secret"}],"count":1}`,
	} {
		ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) { return jsonResp(200, body), nil }}
		e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
		res := e.Execute(context.Background(), sqliCmd("benign-home"))
		s := res.Details.SQLi.Sends[0]
		if s.Error != "SCHEMA" {
			t.Fatalf("%s: error=%q rows=%d, want SCHEMA (a malformed 200 must not count as clean)", name, s.Error, s.Rows)
		}
		if res.Status != "FAILED" {
			t.Fatalf("%s: status=%s, want FAILED (every send errored)", name, res.Status)
		}
	}
}

// ZR42-03: a slow response must never let the next send fire early. With the ticker, a tick buffered during a
// slow first response produced a sub-interval burst; scheduling from the actual dispatch time prevents that.
func TestSQLiExecutorPacingNeverBurstsAfterSlowResponse(t *testing.T) {
	if testing.Short() {
		t.Skip("timing test")
	}
	const pace = 40 * time.Millisecond
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		if n == 1 {
			time.Sleep(3 * pace) // first response is much slower than the pace interval
		}
		return jsonResp(200, `{"results":[],"count":0}`), nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 4, MaxCommandSec: 5, Transport: ft, pace: pace, Resolver: privateResolver}
	res := e.Execute(context.Background(), sqliCmd("benign-home"))
	if res.Details.RequestsSent != 4 {
		t.Fatalf("sends %d, want 4", res.Details.RequestsSent)
	}
	var prev time.Time
	for i, s := range res.Details.SQLi.Sends {
		at, err := time.Parse(time.RFC3339Nano, s.StartedAt)
		if err != nil {
			t.Fatalf("send %d bad startedAt %q: %v", i, s.StartedAt, err)
		}
		if i > 0 {
			if gap := at.Sub(prev); gap < pace-5*time.Millisecond {
				t.Fatalf("send %d fired %v after the previous one, under the %v pace (burst)", i, gap, pace)
			}
		}
		prev = at
	}
}

// ZR42-04: the resolved peer must be a private cluster address. A public (TEST-NET), loopback, or unresolvable
// endpoint is rejected before any send; a private address proceeds.
func TestSQLiExecutorPeerCheck(t *testing.T) {
	sent := false
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		sent = true
		return jsonResp(200, `{"results":[],"count":0}`), nil
	}}
	reject := map[string]func(context.Context, string) ([]net.IP, error){
		"public-testnet": func(context.Context, string) ([]net.IP, error) { return []net.IP{net.IPv4(203, 0, 113, 10)}, nil },
		"loopback":       func(context.Context, string) ([]net.IP, error) { return []net.IP{net.IPv4(127, 0, 0, 1)}, nil },
		"empty":          func(context.Context, string) ([]net.IP, error) { return nil, nil },
		"error":          func(context.Context, string) ([]net.IP, error) { return nil, io.ErrUnexpectedEOF },
		"mixed": func(context.Context, string) ([]net.IP, error) {
			return []net.IP{net.IPv4(10, 0, 0, 1), net.IPv4(8, 8, 8, 8)}, nil
		},
	}
	for name, resolver := range reject {
		e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: resolver}
		res := e.Execute(context.Background(), sqliCmd("benign-home"))
		if res.Status != "REJECTED" || res.Details.ErrorMessage != "SQLI_GUARD:peer" {
			t.Fatalf("%s: status=%s msg=%q, want REJECTED SQLI_GUARD:peer", name, res.Status, res.Details.ErrorMessage)
		}
	}
	if sent {
		t.Fatal("a rejected peer must send nothing")
	}
	// A private address proceeds and sends.
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 1, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	if res := e.Execute(context.Background(), sqliCmd("benign-home")); res.Status != "SUCCESS" {
		t.Fatalf("private peer rejected: %s %s", res.Status, res.Details.ErrorMessage)
	}
}

type peerConn struct {
	net.Conn
	peer *net.TCPAddr
}

func (c peerConn) RemoteAddr() net.Addr { return c.peer }

func TestSQLiPinnedDialUsesApprovedNumericPeer(t *testing.T) {
	approved := net.IPv4(10, 1, 2, 3)
	var dialed string
	e := &SQLIExecutor{ApprovedIP: approved}
	e.DialContext = func(_ context.Context, network, address string) (net.Conn, error) {
		dialed = address
		client, server := net.Pipe()
		_ = server.Close()
		return peerConn{Conn: client, peer: &net.TCPAddr{IP: approved, Port: 8000}}, nil
	}
	dial := e.pinnedDial("zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000", approved)
	conn, err := dial(context.Background(), "tcp", "zer41-private-ingress.zd-sqli-lab.svc.cluster.local:8000")
	if err != nil {
		t.Fatal(err)
	}
	_ = conn.Close()
	if dialed != "10.1.2.3:8000" {
		t.Fatalf("dial was not pinned to approved numeric peer: %q", dialed)
	}
	if _, err := dial(context.Background(), "tcp", "fixture-copy.zd-sqli-lab.svc.cluster.local:8000"); err == nil {
		t.Fatal("unapproved authority reached dialer")
	}
}

// ZR42-05: each send carries a neutral correlation id and records the fixture's response id, the join keys to
// the fixture access log and its source-IP record.
func TestSQLiExecutorRecordsCorrelationAndResponseID(t *testing.T) {
	ft := &fakeTransport{handle: func(n int, r *http.Request) (*http.Response, error) {
		if got := r.Header.Get("X-Correlation-Id"); got == "" {
			t.Error("request carried no X-Correlation-Id")
		}
		resp := jsonResp(200, `{"results":[],"count":0}`)
		resp.Header.Set("X-Request-Id", "fixture-req-7")
		return resp, nil
	}}
	e := &SQLIExecutor{ApprovedIP: net.IPv4(10, 1, 2, 3), MaxSends: 2, MaxCommandSec: 5, Transport: ft, pace: time.Millisecond, Resolver: privateResolver}
	cmd := sqliCmd("benign-home")
	res := e.Execute(context.Background(), cmd)
	if res.Details.SQLi.ClockID == "" || res.Details.SQLi.WindowStart == "" {
		t.Fatalf("observation missing clock/window: %+v", res.Details.SQLi)
	}
	for i, s := range res.Details.SQLi.Sends {
		if s.Seq != i+1 || s.RequestID != cmd.CommandID+"/"+itoa(i+1) {
			t.Fatalf("send %d requestId=%q seq=%d", i, s.RequestID, s.Seq)
		}
		if s.ResponseID != "fixture-req-7" {
			t.Fatalf("send %d responseId=%q, want fixture-req-7", i, s.ResponseID)
		}
		if s.ObservedAt == "" {
			t.Fatalf("send %d missing observedAt", i)
		}
	}
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	var b [20]byte
	i := len(b)
	for n > 0 {
		i--
		b[i] = byte('0' + n%10)
		n /= 10
	}
	return string(b[i:])
}
