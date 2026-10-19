package kafka

import (
	"context"
	"errors"
	kgo "github.com/segmentio/kafka-go"
	"testing"
)

type fakeReader struct {
	fetches, commits int
	fail             bool
}

func (f *fakeReader) FetchMessage(_ context.Context) (kgo.Message, error) {
	f.fetches++
	return kgo.Message{Value: []byte("opaque-command"), Offset: 41}, nil
}
func (f *fakeReader) CommitMessages(_ context.Context, m ...kgo.Message) error {
	f.commits++
	if len(m) != 1 || m[0].Offset != 41 {
		return errors.New("wrong offset")
	}
	if f.fail {
		return errors.New("offline commit failure")
	}
	return nil
}
func (f *fakeReader) Close() error { return nil }
func TestPollDoesNotAckBeforeAdmissionOrPublication(t *testing.T) {
	reader := &fakeReader{}
	consumer := Consumer{reader: reader}
	raw, err := consumer.Poll(context.Background(), 1000)
	if err != nil || string(raw) != "opaque-command" || reader.commits != 0 {
		t.Fatal(raw, err, reader)
	}
	if _, err = consumer.Poll(context.Background(), 1000); err == nil || reader.fetches != 1 {
		t.Fatal("unacknowledged message skipped")
	}
	reader.fail = true
	if err = consumer.Ack(context.Background()); err == nil {
		t.Fatal("commit failure hidden")
	}
	if _, err = consumer.Poll(context.Background(), 1000); err == nil || reader.fetches != 1 {
		t.Fatal("failed ack skipped")
	}
	reader.fail = false
	if err = consumer.Ack(context.Background()); err != nil {
		t.Fatal(err)
	}
	if _, err = consumer.Poll(context.Background(), 1000); err != nil || reader.fetches != 2 {
		t.Fatal("valid ack did not release pending", err)
	}
}
