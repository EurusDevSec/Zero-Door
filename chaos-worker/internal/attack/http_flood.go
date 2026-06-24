package attack

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"sync"
	"sync/atomic"
	"time"

	"github.com/google/uuid"
)

// HTTPFloodExecutor implements a Layer-7 HTTP flood (DDoS simulation).
// It spawns N goroutines, each sending HTTP GET requests to the target URL
// as fast as possible (up to RPS limit) until the context deadline is reached.
type HTTPFloodExecutor struct {
	// MaxConcurrency is the upper cap on goroutines regardless of command params.
	MaxConcurrency int
	// GlobalMaxSec is the kill-switch duration from config.
	GlobalMaxSec int
}

func (e *HTTPFloodExecutor) Execute(ctx context.Context, cmd AttackCommand) AttackResult {
	result := AttackResult{
		ResultID:   uuid.New().String(),
		CommandID:  cmd.CommandID,
		Timestamp:  NowISO(),
		Source:     "chaos-worker",
		AttackType: cmd.AttackType,
	}

	targetURL := cmd.Target.URL
	if targetURL == "" {
		// Build default URL from service name
		targetURL = fmt.Sprintf("http://%s.%s.svc.cluster.local", cmd.Target.Service, cmd.Target.Namespace)
	}

	duration := EffectiveDuration(cmd, e.GlobalMaxSec)
	concurrency := cmd.Parameters.Concurrency
	if concurrency <= 0 || concurrency > e.MaxConcurrency {
		concurrency = e.MaxConcurrency
	}

	slog.Info("HTTP Flood attack starting",
		"commandId", cmd.CommandID,
		"target", targetURL,
		"concurrency", concurrency,
		"duration", duration,
	)

	start := time.Now()
	var totalRequests int64

	// Honour existing context AND add our own deadline
	attackCtx, cancel := context.WithTimeout(ctx, duration)
	defer cancel()

	client := &http.Client{
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			MaxIdleConnsPerHost: concurrency,
		},
	}

	var wg sync.WaitGroup
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-attackCtx.Done():
					return
				default:
					req, err := http.NewRequestWithContext(attackCtx, http.MethodGet, targetURL, nil)
					if err != nil {
						continue
					}
					resp, err := client.Do(req)
					if err == nil {
						io.Copy(io.Discard, resp.Body) //nolint:errcheck
						resp.Body.Close()
					}
					atomic.AddInt64(&totalRequests, 1)
				}
			}
		}()
	}

	wg.Wait()

	elapsed := time.Since(start)
	sent := int(atomic.LoadInt64(&totalRequests))

	slog.Info("HTTP Flood attack completed",
		"commandId", cmd.CommandID,
		"requestsSent", sent,
		"elapsedMs", elapsed.Milliseconds(),
	)

	result.Status = "SUCCESS"
	result.DurationMs = elapsed.Milliseconds()
	result.Details = ResultDetails{RequestsSent: sent}
	return result
}
