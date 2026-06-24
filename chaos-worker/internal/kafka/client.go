// Package kafka provides Kafka consumer and producer wrappers for the Chaos Worker.
// Uses segmentio/kafka-go (pure Go — no CGO required).
package kafka

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"time"

	kgo "github.com/segmentio/kafka-go"
)

// ---- Consumer ----

// Consumer wraps a kafka-go Reader for reading attack commands.
type Consumer struct {
	reader *kgo.Reader
}

// NewConsumer creates a new Kafka consumer subscribed to the given topic.
func NewConsumer(bootstrapServers, groupID, topic string) (*Consumer, error) {
	reader := kgo.NewReader(kgo.ReaderConfig{
		Brokers:        []string{bootstrapServers},
		GroupID:        groupID,
		Topic:          topic,
		MinBytes:       10e3,   // 10KB
		MaxBytes:       10e6,   // 10MB
		CommitInterval: time.Second,
		StartOffset:    kgo.LastOffset, // Only process new commands
	})

	slog.Info("Kafka consumer initialized", "topic", topic, "group", groupID, "broker", bootstrapServers)
	return &Consumer{reader: reader}, nil
}

// Poll fetches the next message, returning raw bytes.
// Returns nil, nil if context is cancelled without error.
func (c *Consumer) Poll(ctx context.Context, timeoutMs int) ([]byte, error) {
	fetchCtx, cancel := context.WithTimeout(ctx, time.Duration(timeoutMs)*time.Millisecond)
	defer cancel()

	msg, err := c.reader.FetchMessage(fetchCtx)
	if err != nil {
		if err == context.DeadlineExceeded || err == context.Canceled {
			return nil, nil // no message available within timeout — normal
		}
		return nil, fmt.Errorf("kafka fetch error: %w", err)
	}

	// Commit offset
	if commitErr := c.reader.CommitMessages(ctx, msg); commitErr != nil {
		slog.Warn("Failed to commit Kafka offset", "error", commitErr)
	}

	slog.Debug("Kafka message received",
		"topic", msg.Topic,
		"partition", msg.Partition,
		"offset", msg.Offset,
	)

	return msg.Value, nil
}

// Close shuts down the consumer cleanly.
func (c *Consumer) Close() error {
	return c.reader.Close()
}

// ---- Producer ----

// Producer wraps a kafka-go Writer for sending attack results.
type Producer struct {
	writer *kgo.Writer
	topic  string
}

// NewProducer creates a new Kafka producer for publishing attack results.
func NewProducer(bootstrapServers, topic string) (*Producer, error) {
	writer := &kgo.Writer{
		Addr:         kgo.TCP(bootstrapServers),
		Topic:        topic,
		Balancer:     &kgo.LeastBytes{},
		RequiredAcks: kgo.RequireAll,
		MaxAttempts:  5,
		BatchTimeout: 100 * time.Millisecond,
	}

	slog.Info("Kafka producer initialized", "topic", topic, "broker", bootstrapServers)
	return &Producer{writer: writer, topic: topic}, nil
}

// Send serialises value as JSON and publishes it to the configured topic.
func (p *Producer) Send(value any) error {
	data, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("failed to marshal message: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	return p.writer.WriteMessages(ctx, kgo.Message{
		Value: data,
		Time:  time.Now().UTC(),
	})
}

// Flush is a no-op for kafka-go (writes are synchronous by default).
func (p *Producer) Flush(timeoutMs int) {}

// Close shuts down the producer cleanly.
func (p *Producer) Close() {
	if err := p.writer.Close(); err != nil {
		slog.Warn("Error closing Kafka writer", "error", err)
	}
}
