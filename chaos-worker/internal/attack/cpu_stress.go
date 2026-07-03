package attack

import (
	"context"
	"fmt"
	"log/slog"
	"time"

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
				"chaos-command-id": cmd.CommandID[:8],
			},
		},
		Spec: corev1.PodSpec{
			RestartPolicy: corev1.RestartPolicyNever,
			// Run as non-root for security
			SecurityContext: &corev1.PodSecurityContext{
				RunAsNonRoot: boolPtr(true),
				RunAsUser:    int64Ptr(65534),
			},
			Containers: []corev1.Container{
				{
					Name:    "stress",
					Image:   "progrium/stress",
					Command: []string{"/usr/bin/stress"},
					Args:    stressArgs,
					Resources: corev1.ResourceRequirements{
						Requests: corev1.ResourceList{
							corev1.ResourceCPU:    resource.MustParse("100m"),
							corev1.ResourceMemory: resource.MustParse("64Mi"),
						},
						Limits: corev1.ResourceList{
							corev1.ResourceCPU:    resource.MustParse("500m"),
							corev1.ResourceMemory: resource.MustParse("256Mi"),
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
	_, err := e.KubeClient.CoreV1().Pods(namespace).Create(ctx, pod, metav1.CreateOptions{})
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
	case <-ctx.Done():
	case <-time.After(duration):
	}

	// Auto-cleanup: delete the stress pod
	delErr := e.KubeClient.CoreV1().Pods(namespace).Delete(ctx, podName, metav1.DeleteOptions{})
	if delErr != nil {
		slog.Warn("Failed to auto-cleanup stress pod", "podName", podName, "error", delErr)
	} else {
		slog.Info("Stress pod auto-cleaned up", "podName", podName)
	}

	elapsed := time.Since(start)

	result.Status = "SUCCESS"
	result.DurationMs = elapsed.Milliseconds()
	result.Details = ResultDetails{}
	return result
}

func boolPtr(b bool) *bool { return &b }
func int64Ptr(i int64) *int64 { return &i }
