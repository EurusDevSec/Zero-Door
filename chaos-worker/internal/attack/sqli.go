package attack

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"sort"
	"strconv"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
	"github.com/google/uuid"
)

// Locked SQLi command catalog for ZER-42. Every entry is a read-only catalog search against the ZER-41
// fixture, reusing only patterns already reviewed in ZER-41 (tests/fixtures/zer41/expected.json). The
// executor may only URL-encode one entry's Category into the `category` query parameter of SQLiSearchPath;
// it never accepts raw SQL, raw payloads, arbitrary method/path/headers/URL, filesystem/shell, host/schema
// scans, DB writes, or any technique beyond these entries. Destructive strings the fixture already rejects
// (stacked DELETE, UNION returning a non-text value) are deliberately NOT in this catalog: ZER-41 proved the
// fixture refuses them at the service layer, and the executor needs no capability to emit them.
const (
	SQLiCatalogVersion = "zd-sqli-catalog/1"
	SQLiSearchPath     = "/fixture/catalog/search" // must match validation.sqliSearchPath
	SQLiNamespace      = "zd-sqli-lab"
	SQLiService        = "sqli-fixture"

	// Design ceilings (ZER-42 §279). Trusted config may lower these, never raise them.
	SQLiConcurrency   = 1      // one in-flight request, never more
	SQLiMaxRPS        = 1      // at most one send per second
	SQLiMaxSends      = 20     // total sends per command, counting every retry/redirect (none are made)
	SQLiPerCommandSec = 30     // wall-clock budget for one command
	SQLiMaxResponse   = 262144 // 256 KiB response read cap
	SQLiRequestMs     = 3000   // per-request timeout, also clamped by the remaining command deadline
)

// SQLiTemplate is one locked catalog entry. Kind is "injection" (the single disclosure template whose oracle
// is the restricted seed rows) or "benign" (an ordinary public-category search used as control traffic on the
// same route). The oracle (which restricted rows prove effect) lives with the H-plane evaluator's criteria,
// not here, so the executor stays a neutral sender that cannot read the answer key.
type SQLiTemplate struct {
	ID       string
	Category string
	Kind     string
}

var sqliCatalog = map[string]SQLiTemplate{
	// The one disclosure template, verbatim from ZER-41 expected.json ("injection.category"). On the
	// vulnerable profile it returns the restricted seed rows; on the safe profile it returns none.
	"disclose-restricted": {ID: "disclose-restricted", Category: "zzz' OR visibility='restricted' --", Kind: "injection"},
	// Benign controls: ordinary public-category searches on the same route (ZER-41 expected.json benign).
	"benign-apparel":     {ID: "benign-apparel", Category: "apparel", Kind: "benign"},
	"benign-home":        {ID: "benign-home", Category: "home", Kind: "benign"},
	"benign-electronics": {ID: "benign-electronics", Category: "electronics", Kind: "benign"},
}

// LookupSQLiTemplate returns the locked catalog entry for id, or ok=false if id is not in the catalog.
func LookupSQLiTemplate(id string) (SQLiTemplate, bool) {
	t, ok := sqliCatalog[id]
	return t, ok
}

// SQLiTemplateIDs returns the catalog ids in sorted order (stable for config, docs and tests).
func SQLiTemplateIDs() []string {
	ids := make([]string, 0, len(sqliCatalog))
	for id := range sqliCatalog {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	return ids
}

// SQLiSend is one raw send observation: its ordinal and wall-clock stamps on the executor clock, the
// correlation id sent / the fixture request id returned (the join keys to the fixture access log and its
// source-IP record), the HTTP status, how many rows the fixture returned, how many of them were non-public,
// and (bounded) which SKUs those were. Rows/RestrictedRows are -1 when unknown (no response, non-200, or an
// unparseable/malformed body). Error is a neutral short code, never a payload or a SQL string. StartedAt is
// when the send was dispatched; ObservedAt is when its response or error was observed — the latter is the real
// evidence instant the H-plane evaluator stamps as t_eff for a disclosing send.
type SQLiSend struct {
	Seq            int      `json:"seq"`
	StartedAt      string   `json:"startedAt"`
	ObservedAt     string   `json:"observedAt"`
	RequestID      string   `json:"requestId,omitempty"`
	ResponseID     string   `json:"responseId,omitempty"`
	Status         int      `json:"status"`
	Rows           int      `json:"rows"`
	RestrictedRows int      `json:"restrictedRows"`
	RestrictedSKUs []string `json:"restrictedSkus,omitempty"`
	Error          string   `json:"error,omitempty"`
}

// SQLiObservation is the executor's whole raw result for one command: which locked template it replayed, the
// executor clock identity (so the evaluator stamps evidence on a named clock, not "clock-unknown"), the command
// window start T_req, and the per-send observations. It is plane-F evidence only; it carries no oracle, no
// expected ids and no verdict.
type SQLiObservation struct {
	TemplateID  string     `json:"templateId"`
	Kind        string     `json:"kind"`
	ClockID     string     `json:"clockId"`
	ClockSource string     `json:"clockSource"`
	WindowStart string     `json:"windowStart"`
	Sends       []SQLiSend `json:"sends"`
}

// SQLiClockID / SQLiClockSource identify the executor's time axis on each observation. The offline/loopback
// executor makes no cross-host clock claim, so the source is UNKNOWN (a contract clock_source enum value); a
// lab run that binds a shared/synced clock sets a verified id out of band.
const (
	SQLiClockID     = "chaos-worker-local"
	SQLiClockSource = "UNKNOWN"
)

// SQLIExecutor replays one locked catalog template against the configured fixture endpoint. It honours an
// absolute command deadline, paces at one send per second, never retries or follows redirects, bounds each
// response, and stops creating sends the moment ctx is cancelled (SIGTERM). It spawns no goroutine of its own
// (concurrency is always one), so a cancelled command leaves nothing running.
type SQLIExecutor struct {
	MaxSends      int               // <= SQLiMaxSends; from the policy capability
	MaxCommandSec int               // <= SQLiPerCommandSec; from the policy capability
	Transport     http.RoundTripper // nil in production; a fake transport in offline tests
	Now           func() time.Time  // nil -> time.Now
	// ApprovedIP is the exact private ingress Service IP captured by the operator's
	// runtime preflight. DNS alone is not authority to connect to another private IP.
	ApprovedIP net.IP
	// DialContext is a test seam. Production always dials a numeric ApprovedIP and
	// verifies the connected peer; it never resolves the hostname a second time.
	DialContext func(context.Context, string, string) (net.Conn, error)
	// Resolver returns the addresses the endpoint host resolves to; the preflight peer check requires every one
	// to be a private cluster address (no public, loopback or link-local). nil => net.DefaultResolver.LookupIP.
	// A fake resolver feeds offline tests; production binds the checked IP to the dial.
	Resolver func(ctx context.Context, host string) ([]net.IP, error)
	pace     time.Duration // test-only override of the 1/rps send interval; 0 => time.Second/SQLiMaxRPS
}

func (e *SQLIExecutor) Execute(ctx context.Context, cmd AttackCommand) AttackResult {
	now := e.Now
	if now == nil {
		now = time.Now
	}
	result := AttackResult{ResultID: uuid.NewString(), CommandID: cmd.CommandID, Timestamp: NowISO(),
		Source: "chaos-worker", AttackType: cmd.AttackType, Status: "REJECTED"}

	// Re-derive and re-validate everything from the command; never trust that admission already ran. A failure
	// here is a guard rejection with zero sends, not a silent no-effect.
	base, err := validation.ValidateSQLiEndpoint(cmd.Target.URL)
	if err != nil {
		result.Details.ErrorMessage = "SQLI_GUARD:endpoint"
		return result
	}
	id, _ := cmd.Parameters.CustomParams["template"].(string)
	tmpl, ok := LookupSQLiTemplate(id)
	if !ok || len(cmd.Parameters.CustomParams) != 1 || cmd.Parameters.Concurrency != SQLiConcurrency {
		result.Details.ErrorMessage = "SQLI_GUARD:command"
		return result
	}
	if e.MaxSends < 1 || e.MaxSends > SQLiMaxSends {
		result.Details.ErrorMessage = "SQLI_GUARD:sends"
		return result
	}
	maxSec := e.MaxCommandSec
	if maxSec < 1 || maxSec > SQLiPerCommandSec {
		result.Details.ErrorMessage = "SQLI_GUARD:budget"
		return result
	}
	if cmd.Parameters.DurationSec >= 1 && cmd.Parameters.DurationSec < maxSec {
		maxSec = cmd.Parameters.DurationSec
	}

	// Build the final URL by URL-encoding the catalog category into the one `category` parameter. No other part
	// of the URL is ever templated, so the executor cannot be steered to another path, host or parameter.
	u, err := url.Parse(base)
	if err != nil {
		result.Details.ErrorMessage = "SQLI_GUARD:url"
		return result
	}
	q := url.Values{}
	q.Set("category", tmpl.Category)
	u.RawQuery = q.Encode()
	target := u.String()

	// Preflight the endpoint host: every resolved address must be a private cluster address. This rejects a
	// trusted-but-wrong config that points at a public (e.g. TEST-NET), loopback or link-local address before any
	// send, so the executor can only reach the in-cluster ingress, never bypass the lab's IP observation point.
	start := now()
	deadline := start.Add(time.Duration(maxSec) * time.Second)
	bounded, cancel := context.WithDeadline(ctx, deadline)
	defer cancel()
	peer, err := e.checkPeer(bounded, u.Hostname())
	if err != nil {
		result.Details.ErrorMessage = "SQLI_GUARD:peer"
		result.DurationMs = time.Since(start).Milliseconds()
		return result
	}

	obs := &SQLiObservation{TemplateID: tmpl.ID, Kind: tmpl.Kind,
		ClockID: SQLiClockID, ClockSource: SQLiClockSource, WindowStart: isoAt(start)}

	transport := e.Transport
	if transport == nil {
		transport = &http.Transport{DisableKeepAlives: true, MaxConnsPerHost: 1,
			DialContext: e.pinnedDial(u.Host, peer)}
	}
	if closer, ok := transport.(interface{ CloseIdleConnections() }); ok {
		defer closer.CloseIdleConnections()
	}
	client := &http.Client{Transport: transport,
		CheckRedirect: func(_ *http.Request, _ []*http.Request) error { return http.ErrUseLastResponse }}

	interval := e.pace
	if interval <= 0 {
		interval = time.Second / time.Duration(SQLiMaxRPS)
	}
	timer := time.NewTimer(0)
	if !timer.Stop() {
		<-timer.C
	}
	defer timer.Stop()

	sends := 0
	var nextAt time.Time // the earliest the next send may be dispatched (prev dispatch + interval)
loop:
	for sends < e.MaxSends {
		if bounded.Err() != nil {
			break
		}
		if sends > 0 { // pace from the actual previous dispatch, so a slow response never lets the next fire early
			if wait := nextAt.Sub(now()); wait > 0 {
				timer.Reset(wait)
				select {
				case <-bounded.Done():
					if !timer.Stop() {
						<-timer.C
					}
					break loop // cancelled/deadline: stop creating new sends, no accumulated catch-up
				case <-timer.C:
				}
				if bounded.Err() != nil {
					break
				}
			}
		}
		remaining := time.Until(deadline)
		if remaining <= 0 {
			break
		}
		reqTimeout := time.Duration(SQLiRequestMs) * time.Millisecond
		if remaining < reqTimeout {
			reqTimeout = remaining
		}
		sends++
		sendStart := now()
		nextAt = sendStart.Add(interval) // schedule the next send from this dispatch, not from a fixed ticker
		reqCtx, reqCancel := context.WithTimeout(bounded, reqTimeout)
		send := e.one(reqCtx, client, target, cmd.CommandID, sends, sendStart, now)
		reqCancel()
		obs.Sends = append(obs.Sends, send)
	}

	result.DurationMs = time.Since(start).Milliseconds()
	result.Details.RequestsSent = sends
	result.Details.SQLi = obs
	switch {
	case ctx.Err() != nil:
		result.Status = "TIMEOUT"
		result.Details.ErrorMessage = "PARENT_CANCELLED"
	case sends == 0:
		result.Status = "FAILED"
		result.Details.ErrorMessage = "SQLI_NO_SEND"
	default:
		// SUCCESS describes send execution only. It is never fault-effect evidence; the H-plane evaluator reads
		// Details.SQLi and decides EFFECT_EVALUATED against its own oracle. An error on every send is reported as
		// FAILED (a transport/parse failure must not be mistaken for a clean "no restricted rows" observation).
		result.Status = "SUCCESS"
		allErrored := true
		for _, s := range obs.Sends {
			if s.Error == "" {
				allErrored = false
				break
			}
		}
		if allErrored {
			result.Status = "FAILED"
			result.Details.ErrorMessage = "SQLI_ALL_SENDS_ERRORED"
		}
	}
	return result
}

// one performs a single bounded GET and returns its raw observation. It stamps the send's ordinal and times,
// carries a neutral bounded correlation id and records the fixture's response id (the join keys to the fixture
// access log and source-IP record), reads at most SQLiMaxResponse bytes, never follows a redirect, and derives
// the restricted-row evidence only from a well-formed catalog response (an HTTP 200 whose body is not a valid
// catalog result is a SCHEMA error, never a clean "no restricted rows" observation).
func (e *SQLIExecutor) one(ctx context.Context, client *http.Client, target, commandID string, seq int, sendStart time.Time, now func() time.Time) (send SQLiSend) {
	correlation := commandID + "/" + strconv.Itoa(seq)
	send = SQLiSend{Seq: seq, StartedAt: isoAt(sendStart), RequestID: correlation, Rows: -1, RestrictedRows: -1}
	// Stamp after body reading/validation (or the terminal error), never at headers.
	defer func() { send.ObservedAt = isoAt(now()) }()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, target, nil)
	if err != nil {
		send.Error = "REQUEST_BUILD"
		return send
	}
	req.Header.Set("X-Correlation-Id", correlation)
	resp, err := client.Do(req)
	if err != nil {
		send.Error = "TRANSPORT"
		return send
	}
	defer resp.Body.Close()
	send.Status = resp.StatusCode
	send.ResponseID = resp.Header.Get("X-Request-Id")
	body, err := io.ReadAll(io.LimitReader(resp.Body, SQLiMaxResponse+1))
	if err != nil {
		send.Error = "READ"
		return send
	}
	if len(body) > SQLiMaxResponse {
		send.Error = "RESPONSE_TOO_LARGE"
		return send
	}
	if resp.StatusCode == http.StatusOK {
		// Pointers distinguish an absent field from a zero value: a missing/null `results` or `count`, a negative
		// or mismatched count, or a row missing sku/visibility is a malformed body, not an empty clean result.
		var parsed struct {
			Results *[]struct {
				SKU        *string `json:"sku"`
				Visibility *string `json:"visibility"`
			} `json:"results"`
			Count *int `json:"count"`
		}
		if json.Unmarshal(body, &parsed) != nil {
			send.Error = "PARSE"
			return send
		}
		if parsed.Results == nil || parsed.Count == nil || *parsed.Count < 0 || *parsed.Count != len(*parsed.Results) {
			send.Error = "SCHEMA"
			return send
		}
		restricted := []string{}
		for _, r := range *parsed.Results {
			if r.SKU == nil || *r.SKU == "" || r.Visibility == nil ||
				(*r.Visibility != "public" && *r.Visibility != "restricted") {
				send.Error = "SCHEMA"
				return send
			}
			if *r.Visibility != "public" {
				restricted = append(restricted, *r.SKU)
			}
		}
		send.Rows = *parsed.Count
		send.RestrictedRows = len(restricted)
		if len(restricted) > 0 {
			send.RestrictedSKUs = restricted
		}
	}
	return send
}

// isoAt floors to UTC milliseconds as required by the locked event contract.
func isoAt(t time.Time) string {
	return t.UTC().Truncate(time.Millisecond).Format("2006-01-02T15:04:05.000Z")
}

// checkPeer resolves host and requires every address to be a private cluster address. An empty result, a
// resolver error, or any public/loopback/link-local/multicast/unspecified address fails closed.
func (e *SQLIExecutor) checkPeer(ctx context.Context, host string) (net.IP, error) {
	if !isPrivateClusterIP(e.ApprovedIP) {
		return nil, &net.AddrError{Err: "missing approved ingress IP", Addr: host}
	}
	lookup := e.Resolver
	if lookup == nil {
		lookup = func(ctx context.Context, h string) ([]net.IP, error) {
			return net.DefaultResolver.LookupIP(ctx, "ip", h)
		}
	}
	ips, err := lookup(ctx, host)
	if err != nil {
		return nil, err
	}
	if len(ips) == 0 {
		return nil, &net.AddrError{Err: "no addresses", Addr: host}
	}
	for _, ip := range ips {
		if !isPrivateClusterIP(ip) || !ip.Equal(e.ApprovedIP) {
			return nil, &net.AddrError{Err: "address differs from approved ingress", Addr: ip.String()}
		}
	}
	return append(net.IP(nil), e.ApprovedIP...), nil
}

func (e *SQLIExecutor) pinnedDial(authority string, peer net.IP) func(context.Context, string, string) (net.Conn, error) {
	return func(ctx context.Context, network, address string) (net.Conn, error) {
		if address != authority || network != "tcp" || ctx.Err() != nil {
			return nil, fmt.Errorf("SQLI_DIAL_AUTHORITY")
		}
		_, port, err := net.SplitHostPort(address)
		if err != nil {
			return nil, err
		}
		dial := e.DialContext
		if dial == nil {
			dial = (&net.Dialer{}).DialContext
		}
		conn, err := dial(ctx, "tcp", net.JoinHostPort(peer.String(), port))
		if err != nil {
			return nil, err
		}
		remote, ok := conn.RemoteAddr().(*net.TCPAddr)
		if !ok || !remote.IP.Equal(peer) || remote.Port != 8000 {
			_ = conn.Close()
			return nil, fmt.Errorf("SQLI_DIAL_PEER")
		}
		return conn, nil
	}
}

// isPrivateClusterIP reports whether ip is a private unicast address usable inside the lab cluster: RFC1918 or
// unique-local (via net.IP.IsPrivate), and never loopback, link-local, multicast or the unspecified address.
// A public address such as TEST-NET 203.0.113.0/24 and loopback 127.0.0.1 both fail.
func isPrivateClusterIP(ip net.IP) bool {
	if ip == nil || ip.IsLoopback() || ip.IsLinkLocalUnicast() || ip.IsLinkLocalMulticast() ||
		ip.IsMulticast() || ip.IsUnspecified() {
		return false
	}
	return ip.IsPrivate()
}
