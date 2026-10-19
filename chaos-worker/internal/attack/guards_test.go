package attack

import (
	"context"
	"errors"
	"io"
	"net/http"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func TestStrictJSONAndDurations(t *testing.T) {
	for _, raw := range []string{`{"commandId":"a","commandId":"b"}`, `{"unknown":1}`, `{"parameters":{"duration":1.2}}`, `{"parameters":{"duration":NaN}}`, strings.Repeat("[", 18) + "0" + strings.Repeat("]", 18), `{} {}`, strings.Repeat(" ", 32769)} {
		if _, err := ParseCommand([]byte(raw)); err == nil {
			t.Fatal("bad schema accepted", raw)
		}
	}
	c := AttackCommand{Parameters: AttackParameters{DurationSec: 3600}, SafetyLimits: SafetyLimits{MaxDurationSec: 3600}}
	if EffectiveDuration(c, 1) != time.Second {
		t.Fatal("global cap")
	}
	c.SafetyLimits.MaxDurationSec = 1
	if EffectiveDuration(c, 60) != time.Second {
		t.Fatal("command cap")
	}
	for _, bad := range []int{0, -1, int(^uint(0) >> 1)} {
		c.Parameters.DurationSec = bad
		if EffectiveDuration(c, 0) != 0 {
			t.Fatal("invalid config")
		}
	}
}

type transportFunc func(*http.Request) (*http.Response, error)

func (f transportFunc) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func httpCommand() AttackCommand {
	return AttackCommand{CommandID: "short-safe-id", AttackType: "HTTP_FLOOD", Target: AttackTarget{Namespace: "target-app", Service: "frontend"}, Parameters: AttackParameters{DurationSec: 1, Concurrency: 2}, SafetyLimits: SafetyLimits{MaxDurationSec: 100}}
}
func TestHTTPSharedBudgetErrorsAndRedirectDeny(t *testing.T) {
	for _, kind := range []string{"valid", "redirect", "error"} {
		t.Run(kind, func(t *testing.T) {
			var count int32
			ex := HTTPFloodExecutor{MaxConcurrency: 2, GlobalMaxSec: 1, MaxRPS: 5, MaxRequests: 2, Transport: transportFunc(func(req *http.Request) (*http.Response, error) {
				atomic.AddInt32(&count, 1)
				if req.URL.Host != "frontend.target-app.svc.cluster.local" {
					t.Error("redirect escaped")
				}
				if kind == "error" {
					return nil, errors.New("offline")
				}
				code := 200
				headers := http.Header{}
				if kind == "redirect" {
					code = 302
					headers.Set("Location", "http://outside.invalid/")
				}
				return &http.Response{StatusCode: code, Header: headers, Body: io.NopCloser(strings.NewReader("ok")), Request: req}, nil
			})}
			started := time.Now()
			result := ex.Execute(context.Background(), httpCommand())
			if count != 2 || result.Details.RequestsSent != 2 {
				t.Fatal("attempt budget", count, result)
			}
			if time.Since(started) < 390*time.Millisecond {
				t.Fatal("RPS bypass")
			}
			if (kind == "valid" && result.Status != "SUCCESS") || (kind != "valid" && result.Status != "FAILED") {
				t.Fatal(kind, result)
			}
		})
	}
}
func TestHTTPInvalidAndCancelledNoTransport(t *testing.T) {
	var calls int32
	ex := HTTPFloodExecutor{MaxConcurrency: 2, GlobalMaxSec: 1, MaxRPS: 5, MaxRequests: 2, Transport: transportFunc(func(_ *http.Request) (*http.Response, error) {
		atomic.AddInt32(&calls, 1)
		return nil, errors.New("should not call")
	})}
	c := httpCommand()
	c.Target.URL = "http://outside.invalid/"
	if ex.Execute(context.Background(), c).Status != "REJECTED" {
		t.Fatal("target bypass")
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	ex.Execute(ctx, httpCommand())
	if calls != 0 {
		t.Fatal("side effect")
	}
}
