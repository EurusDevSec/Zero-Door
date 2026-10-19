package attack

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"sync"
	"sync/atomic"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
	"github.com/google/uuid"
)

// HTTPFloodExecutor keeps one shared ticker and total-attempt cap across its workers.
// Dispatcher allows only one active command. Error attempts consume the same budget.
type HTTPFloodExecutor struct {
	MaxConcurrency int
	GlobalMaxSec   int
	MaxRPS         int
	MaxRequests    int
	Transport      http.RoundTripper // nil in production; fake transport in offline tests
}

func (e *HTTPFloodExecutor) Execute(ctx context.Context, cmd AttackCommand) AttackResult {
	result := AttackResult{ResultID: uuid.NewString(), CommandID: cmd.CommandID, Timestamp: NowISO(), Source: "chaos-worker", AttackType: cmd.AttackType, Status: "REJECTED"}
	url, err := validation.New([]string{"target-app"}).Resolve(cmd.Target.Namespace, cmd.Target.Service, cmd.Target.URL, true)
	duration := EffectiveDuration(cmd, e.GlobalMaxSec)
	if err != nil || duration <= 0 || e.MaxConcurrency < 1 || e.MaxConcurrency > 50 || e.MaxRPS < 1 || e.MaxRPS > 100 || e.MaxRequests < 1 || e.MaxRequests > 60000 || cmd.Parameters.Concurrency < 1 {
		result.Details.ErrorMessage = "HTTP_GUARD"
		return result
	}
	concurrency := cmd.Parameters.Concurrency
	if concurrency > e.MaxConcurrency {
		concurrency = e.MaxConcurrency
	}
	bounded, cancel := context.WithTimeout(ctx, duration)
	defer cancel()
	transport := e.Transport
	if transport == nil {
		transport = &http.Transport{DisableKeepAlives: true, MaxConnsPerHost: concurrency}
	}
	if closer, ok := transport.(interface{ CloseIdleConnections() }); ok {
		defer closer.CloseIdleConnections()
	}
	client := &http.Client{Timeout: 5 * time.Second, Transport: transport, CheckRedirect: func(_ *http.Request, _ []*http.Request) error { return http.ErrUseLastResponse }}
	ticker := time.NewTicker(time.Second / time.Duration(e.MaxRPS))
	defer ticker.Stop()
	start := time.Now()
	var attempts, failures int64
	var wg sync.WaitGroup
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-bounded.Done():
					return
				case <-ticker.C:
				}
				if bounded.Err() != nil {
					return
				}
				n := atomic.AddInt64(&attempts, 1)
				if n > int64(e.MaxRequests) {
					atomic.AddInt64(&attempts, -1)
					return
				}
				req, err := http.NewRequestWithContext(bounded, http.MethodGet, url, nil)
				if err != nil {
					atomic.AddInt64(&failures, 1)
					continue
				}
				response, err := client.Do(req)
				if err != nil {
					atomic.AddInt64(&failures, 1)
					continue
				}
				// Bound response work as well as request count. Redirects are never followed.
				_, readErr := io.Copy(io.Discard, io.LimitReader(response.Body, 65536))
				closeErr := response.Body.Close()
				if response.StatusCode < 200 || response.StatusCode >= 300 || readErr != nil || closeErr != nil {
					atomic.AddInt64(&failures, 1)
				}
			}
		}()
	}
	wg.Wait()
	result.DurationMs = time.Since(start).Milliseconds()
	result.Details.RequestsSent = int(attempts)
	result.Status = "SUCCESS"
	if ctx.Err() != nil {
		result.Status = "TIMEOUT"
		result.Details.ErrorMessage = "PARENT_CANCELLED"
	} else if attempts == 0 || failures > 0 {
		result.Status = "FAILED"
		result.Details.ErrorMessage = fmt.Sprintf("HTTP_ATTEMPTS_FAILED:%d", failures)
	}
	// SUCCESS describes request execution only. It is never fault-effect or recovery evidence.
	return result
}
