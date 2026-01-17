package lifecycle

import (
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
