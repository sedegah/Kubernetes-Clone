package lifecycle

import (
	"fmt"
	"time"

	"kclone-go/pkg/models"
	"kclone-go/pkg/scheduler"
	"kclone-go/pkg/state"
)

// CreatePod creates a pod and schedules it
func CreatePod(cs *state.ClusterState, spec models.PodSpec) *models.Pod {
	pod := cs.AddPod(spec)
	scheduler.SchedulePendingPods(cs)
	cs.RefreshServiceEndpoints()
	return pod
}

// DeletePod removes a pod
func DeletePod(cs *state.ClusterState, uid string) error {
	err := cs.RemovePod(uid)
	if err != nil {
		return err
	}
	cs.RefreshServiceEndpoints()
	return nil
}

// HealthCheckPod simulates a health check on a pod
func HealthCheckPod(cs *state.ClusterState, uid string) error {
	pods := cs.GetPods()
	for _, pod := range pods {
		if pod.UID == uid {
			if pod.Status.Phase == "Running" {
				pod.Status.Healthy = true
				pod.Status.StartTime = time.Now().Format(time.RFC3339)
				return nil
			}
			return fmt.Errorf("pod %s is not running", uid)
		}
	}
	return fmt.Errorf("pod %s not found", uid)
}

// RestartPod restarts a failed pod
func RestartPod(cs *state.ClusterState, uid string) error {
	pods := cs.GetPods()
	for _, pod := range pods {
		if pod.UID == uid {
			if pod.Spec.RestartPolicy == "Never" {
				return fmt.Errorf("pod %s has restart policy Never", uid)
			}
			
			// Remove and recreate
			DeletePod(cs, uid)
			newPod := cs.AddPod(pod.Spec)
			newPod.Status.RestartCount = pod.Status.RestartCount + 1
			scheduler.SchedulePendingPods(cs)
			cs.RefreshServiceEndpoints()
			return nil
		}
	}
	return fmt.Errorf("pod %s not found", uid)
}
