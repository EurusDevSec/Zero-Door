package attack

import (
	"context"
	"errors"
	"testing"
	"time"

	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes"
	typedcore "k8s.io/client-go/kubernetes/typed/core/v1"
)

// Narrow stubs preserve context/UID options that client-go's action recorder would discard.
type kubeStub struct {
	kubernetes.Interface
	core typedcore.CoreV1Interface
}

func (k kubeStub) CoreV1() typedcore.CoreV1Interface { return k.core }

type coreStub struct {
	typedcore.CoreV1Interface
	pods typedcore.PodInterface
	t    *testing.T
}

func (c coreStub) Pods(namespace string) typedcore.PodInterface {
	if namespace != "target-app" {
		c.t.Fatal("namespace escape", namespace)
	}
	return c.pods
}

type podStub struct {
	typedcore.PodInterface
	create func(context.Context, *corev1.Pod) (*corev1.Pod, error)
	delete func(context.Context, string, metav1.DeleteOptions) error
	list   func(context.Context, metav1.ListOptions) (*corev1.PodList, error)
}

func (p podStub) Create(ctx context.Context, v *corev1.Pod, _ metav1.CreateOptions) (*corev1.Pod, error) {
	return p.create(ctx, v)
}
func (p podStub) Delete(ctx context.Context, name string, options metav1.DeleteOptions) error {
	return p.delete(ctx, name, options)
}
func (p podStub) List(ctx context.Context, options metav1.ListOptions) (*corev1.PodList, error) {
	return p.list(ctx, options)
}
func TestStressCancelUsesFreshBoundedCleanupAndUID(t *testing.T) {
	for _, fail := range []bool{false, true} {
		t.Run(map[bool]string{false: "cleanup", true: "cleanup_failure"}[fail], func(t *testing.T) {
			ctx, cancel := context.WithCancel(context.Background())
			defer cancel()
			created, deleted := 0, 0
			owned := types.UID("only-this-created-uid")
			name := ""
			pods := podStub{create: func(c context.Context, p *corev1.Pod) (*corev1.Pod, error) {
				created++
				name = p.Name
				if p.Spec.ActiveDeadlineSeconds == nil || *p.Spec.ActiveDeadlineSeconds != 1 {
					t.Fatal("pod lifetime not bounded")
				}
				if c.Err() != nil {
					t.Fatal("create cancelled too early")
				}
				cancel()
				p.UID = owned
				return p, nil
			}, delete: func(c context.Context, n string, o metav1.DeleteOptions) error {
				deleted++
				if c.Err() != nil {
					t.Fatal("cleanup reused cancelled context")
				}
				deadline, ok := c.Deadline()
				if !ok || time.Until(deadline) > 5*time.Second {
					t.Fatal("cleanup unbounded")
				}
				if n != name || o.Preconditions == nil || o.Preconditions.UID == nil || *o.Preconditions.UID != owned {
					t.Fatal("cleanup ownership")
				}
				if fail {
					return errors.New("offline cleanup EIO")
				}
				return nil
			}}
			ex := CPUStressExecutor{KubeClient: kubeStub{core: coreStub{pods: pods, t: t}}, GlobalMaxSec: 1}
			cmd := httpCommand()
			cmd.AttackType = "CPU_STRESS"
			cmd.CommandID = "x"
			cmd.Parameters.Intensity = "LOW"
			result := ex.Execute(ctx, cmd)
			if created != 1 || deleted != 1 {
				t.Fatal(created, deleted)
			}
			if fail && result.Status != "FAILED" {
				t.Fatal("cleanup error hidden", result)
			}
			if !fail && result.Status != "TIMEOUT" {
				t.Fatal("cancel hidden", result)
			}
		})
	}
}
func TestPodKillOnlyAllowedServiceSingleUID(t *testing.T) {
	deleted := 0
	uid := types.UID("observed-uid")
	pods := podStub{list: func(c context.Context, o metav1.ListOptions) (*corev1.PodList, error) {
		if o.LabelSelector != "app=frontend" {
			t.Fatal("selector expansion", o)
		}
		return &corev1.PodList{Items: []corev1.Pod{{ObjectMeta: metav1.ObjectMeta{Name: "observed-pod", UID: uid}}, {ObjectMeta: metav1.ObjectMeta{Name: "second", UID: "other"}}}}, nil
	}, delete: func(c context.Context, n string, o metav1.DeleteOptions) error {
		deleted++
		if n != "observed-pod" || o.Preconditions == nil || *o.Preconditions.UID != uid {
			t.Fatal("wrong object")
		}
		return nil
	}}
	ex := PodKillExecutor{KubeClient: kubeStub{core: coreStub{pods: pods, t: t}}, GlobalMaxSec: 1}
	cmd := httpCommand()
	cmd.AttackType = "POD_KILL"
	cmd.Parameters.CustomParams = map[string]any{"labelSelector": ""}
	if ex.Execute(context.Background(), cmd).Status != "REJECTED" || deleted != 0 {
		t.Fatal("selector bypass")
	}
	cmd.Parameters.CustomParams = nil
	if ex.Execute(context.Background(), cmd).Status != "SUCCESS" || deleted != 1 {
		t.Fatal("single uid bound", deleted)
	}
}
