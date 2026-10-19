package attack

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/eurusdevsec/zero-door/chaos-worker/internal/validation"
	"github.com/google/uuid"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
)

// CPUStressExecutor injects an ephemeral stress pod into the target namespace.
// It uses the `progrium/stress` image to consume CPU and memory for the attack duration,
// then automatically cleans up the pod.
type CPUStressExecutor struct {
	KubeClient   kubernetes.Interface
	GlobalMaxSec int
}

func (e *CPUStressExecutor) Execute(ctx context.Context, cmd AttackCommand) AttackResult {
	result := AttackResult{
		ResultID:   uuid.New().String(),
		CommandID:  cmd.CommandID,
		Timestamp:  NowISO(),
		Source:     "chaos-worker",
		AttackType: cmd.AttackType,
	}

	namespace := cmd.Target.Namespace
	duration := EffectiveDuration(cmd, e.GlobalMaxSec)
	if _, err := validation.New([]string{"target-app"}).Resolve(namespace, cmd.Target.Service, cmd.Target.URL, false); err != nil || duration <= 0 {
		result.Status = "REJECTED"
		result.Details.ErrorMessage = "STRESS_GUARD"
		return result
	}

	// Determine CPU workers and memory from intensity
	cpuWorkers := 1
	memWorkers := 0
	switch cmd.Parameters.Intensity {
	case "HIGH":
		cpuWorkers = 4
		memWorkers = 2
	case "MEDIUM":
		cpuWorkers = 2
		memWorkers = 1
	default: // LOW
		cpuWorkers = 1
		memWorkers = 0
	}

	podName := fmt.Sprintf("%s-stress-%s", cmd.Target.Service, uuid.New().String()[:8])

	stressArgs := []string{
		"--cpu", fmt.Sprintf("%d", cpuWorkers),
		"--timeout", fmt.Sprintf("%ds", int(duration.Seconds())),
	}
	if memWorkers > 0 {
		stressArgs = append(stressArgs, "--vm", fmt.Sprintf("%d", memWorkers), "--vm-bytes", "128M")
	}

	pod := &corev1.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      podName,
			Namespace: namespace,
			Labels: map[string]string{
				"app":              "chaos-stress",
				"chaos-worker":     "true",
				"chaos-command-id": cmd.CommandID,
			},
		},
		Spec: corev1.PodSpec{
			RestartPolicy:         corev1.RestartPolicyNever,
			ActiveDeadlineSeconds: int64Ptr(int64(duration.Seconds())),
			// Run as non-root for security
			SecurityContext: &corev1.PodSecurityContext{
				RunAsNonRoot: boolPtr(true),
				RunAsUser:    int64Ptr(65534),
			},
			Containers: []corev1.Container{
				{
					Name:    "stress",
					Image:   "progrium/stress@sha256:e34d56d60f5caae79333cee395aae93b74791d50e3841986420d23c2ee4697bf",
					Command: []string{"/usr/bin/stress"},
					Args:    stressArgs,
					Resources: corev1.ResourceRequirements{
						Requests: corev1.ResourceList{
							corev1.ResourceCPU:    resource.MustParse("100m"),
							corev1.ResourceMemory: resource.MustParse("64Mi"),
						},
						Limits: corev1.ResourceList{
							corev1.ResourceCPU:    resource.MustParse("1000m"),
							corev1.ResourceMemory: resource.MustParse("512Mi"),
						},
					},
				},
			},
		},
	}

	slog.Info("CPU Stress attack starting — creating stress pod",
		"commandId", cmd.CommandID,
		"namespace", namespace,
		"podName", podName,
		"cpuWorkers", cpuWorkers,
		"duration", duration,
	)

	start := time.Now()
	bounded, cancel := context.WithTimeout(ctx, duration)
	defer cancel()
	created, err := e.KubeClient.CoreV1().Pods(namespace).Create(bounded, pod, metav1.CreateOptions{})
	if err != nil {
		errMsg := fmt.Sprintf("Failed to create stress pod '%s': %v", podName, err)
		slog.Error(errMsg, "commandId", cmd.CommandID)
		result.Status = "FAILED"
		result.DurationMs = time.Since(start).Milliseconds()
		result.Details = ResultDetails{ErrorMessage: errMsg}
		return result
	}

	// Wait for attack duration, then clean up
	select {
	case <-bounded.Done():
	case <-time.After(duration):
	}

	// Auto-cleanup: delete the stress pod
	cleanup, cleanupCancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cleanupCancel()
	delErr := e.KubeClient.CoreV1().Pods(namespace).Delete(cleanup, podName, metav1.DeleteOptions{Preconditions: &metav1.Preconditions{UID: &created.UID}})
	if delErr != nil {
		slog.Warn("Failed to auto-cleanup stress pod", "podName", podName, "error", delErr)
	} else {
		slog.Info("Stress pod auto-cleaned up", "podName", podName)
	}

	elapsed := time.Since(start)

	result.Status = "SUCCESS"
	if delErr != nil {
		result.Status = "FAILED"
		result.Details.ErrorMessage = "CLEANUP_FAILED"
	} else if ctx.Err() != nil {
		result.Status = "TIMEOUT"
		result.Details.ErrorMessage = "PARENT_CANCELLED"
	}
	result.DurationMs = elapsed.Milliseconds()
	// Preserve cleanup/cancellation reason.
	return result
}

func boolPtr(b bool) *bool    { return &b }
func int64Ptr(i int64) *int64 { return &i }
