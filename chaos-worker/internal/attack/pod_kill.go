package attack

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
	"github.com/google/uuid"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
)

// PodKillExecutor deletes pods in the target namespace matching a label selector.
// It is the "chaos monkey" attack type — simulating unexpected pod failures to test
// Kubernetes self-healing (Deployment controller creating replacement pods).
type PodKillExecutor struct {
	KubeClient   kubernetes.Interface
	GlobalMaxSec int
}

func (e *PodKillExecutor) Execute(ctx context.Context, cmd AttackCommand) AttackResult {
	result := AttackResult{
		ResultID:   uuid.New().String(),
		CommandID:  cmd.CommandID,
		Timestamp:  NowISO(),
		Source:     "chaos-worker",
		AttackType: cmd.AttackType,
	}

	namespace := cmd.Target.Namespace
	service := cmd.Target.Service

	if _, err := validation.New([]string{"target-app"}).Resolve(namespace, service, cmd.Target.URL, false); err != nil || EffectiveDuration(cmd, e.GlobalMaxSec) <= 0 || len(cmd.Parameters.CustomParams) > 0 {
		result.Status = "REJECTED"
		result.Details.ErrorMessage = "POD_GUARD"
		return result
	}
	bounded, cancel := context.WithTimeout(ctx, EffectiveDuration(cmd, e.GlobalMaxSec))
	defer cancel()
	ctx = bounded
	labelSelector := fmt.Sprintf("app=%s", service)
	killCount := 1

	slog.Info("Pod Kill attack starting",
		"commandId", cmd.CommandID,
		"namespace", namespace,
		"labelSelector", labelSelector,
		"killCount", killCount,
	)

	start := time.Now()

	// List pods matching selector
	podList, err := e.KubeClient.CoreV1().Pods(namespace).List(ctx, metav1.ListOptions{
		LabelSelector: labelSelector,
	})
	if err != nil {
		errMsg := fmt.Sprintf("Failed to list pods with selector '%s' in namespace '%s': %v", labelSelector, namespace, err)
		slog.Error(errMsg, "commandId", cmd.CommandID)
		result.Status = "FAILED"
		result.DurationMs = time.Since(start).Milliseconds()
		result.Details = ResultDetails{ErrorMessage: errMsg}
		return result
	}

	if len(podList.Items) == 0 {
		errMsg := fmt.Sprintf("No pods found with selector '%s' in namespace '%s'", labelSelector, namespace)
		slog.Warn(errMsg, "commandId", cmd.CommandID)
		result.Status = "FAILED"
		result.DurationMs = time.Since(start).Milliseconds()
		result.Details = ResultDetails{ErrorMessage: errMsg}
		return result
	}

	// Kill up to killCount pods
	killed := 0
	gracePeriod := int64(0) // immediate kill
	for i := 0; i < len(podList.Items) && killed < killCount; i++ {
		pod := podList.Items[i]
		// Skip pods that are already terminating
		if pod.DeletionTimestamp != nil {
			slog.Info("Skipping pod already terminating", "pod", pod.Name)
			continue
		}

		err := e.KubeClient.CoreV1().Pods(namespace).Delete(ctx, pod.Name, metav1.DeleteOptions{
			GracePeriodSeconds: &gracePeriod,
			Preconditions:      &metav1.Preconditions{UID: &pod.UID},
		})
		if err != nil {
			slog.Warn("Failed to delete pod", "pod", pod.Name, "error", err)
			continue
		}

		slog.Info("Pod killed successfully", "commandId", cmd.CommandID, "pod", pod.Name, "namespace", namespace)
		killed++
	}

	elapsed := time.Since(start)

	if killed == 0 {
		result.Status = "FAILED"
		result.Details = ResultDetails{ErrorMessage: "No pods could be killed (all terminating or permission denied)"}
	} else {
		result.Status = "SUCCESS"
		result.Details = ResultDetails{PodsKilled: killed}
	}
	result.DurationMs = elapsed.Milliseconds()

	slog.Info("Pod Kill attack completed",
		"commandId", cmd.CommandID,
		"podsKilled", killed,
		"elapsedMs", elapsed.Milliseconds(),
	)

	return result
}
