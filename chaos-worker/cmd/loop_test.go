package main

import (
	"context"
	"errors"
	"github.com/eurusdevsec/zero-door/chaos-worker/internal/attack"
	"reflect"
	"testing"
	"time"
)

type loopConsumer struct {
	steps     *[]string
	stop      context.CancelFunc
	ackError  error
	pollError error
}

func (c *loopConsumer) Poll(ctx context.Context, _ int) ([]byte, error) {
	*c.steps = append(*c.steps, "poll")
	return []byte("fixture"), c.pollError
}
func (c *loopConsumer) Ack(ctx context.Context) error {
	*c.steps = append(*c.steps, "ack")
	if ctx.Err() != nil {
		return ctx.Err()
	}
	deadline, ok := ctx.Deadline()
	if !ok || time.Until(deadline) > 11*time.Second {
		return errors.New("unbounded ack")
	}
	c.stop()
	return c.ackError
}

type loopProducer struct {
	steps *[]string
	err   error
}

func (p *loopProducer) Send(any) error { *p.steps = append(*p.steps, "send"); return p.err }

type loopHandler struct {
	steps *[]string
	stop  context.CancelFunc
}

func (h *loopHandler) Handle(context.Context, []byte) (attack.AttackResult, error) {
	*h.steps = append(*h.steps, "handle")
	h.stop()
	return attack.AttackResult{CommandID: "fixture", Status: "TIMEOUT"}, nil
}

func TestCommandLoopShutdownAndFailureOrdering(t *testing.T) {
	for _, scenario := range []string{"shutdown", "poll", "ledger", "publish", "ack"} {
		t.Run(scenario, func(t *testing.T) {
			ctx, cancel := context.WithCancel(context.Background())
			defer cancel()
			steps := []string{}
			c := &loopConsumer{steps: &steps, stop: cancel}
			p := &loopProducer{steps: &steps}
			h := &loopHandler{steps: &steps, stop: cancel}
			failure := func() error {
				steps = append(steps, "durable")
				if scenario == "ledger" {
					return errors.New("disk")
				}
				return nil
			}
			expected := []string{"poll", "handle", "durable", "send", "ack"}
			code := 1
			switch scenario {
			case "shutdown":
				code = 0
			case "poll":
				c.pollError = errors.New("poll")
				expected = []string{"poll"}
			case "ledger":
				expected = expected[:3]
			case "publish":
				p.err = errors.New("publish")
				expected = expected[:4]
			case "ack":
				c.ackError = errors.New("ack")
			}
			if got := consumeCommands(ctx, c, p, h, failure); got != code {
				t.Fatalf("code=%d want=%d", got, code)
			}
			if !reflect.DeepEqual(steps, expected) {
				t.Fatal(steps, expected)
			}
		})
	}
}
