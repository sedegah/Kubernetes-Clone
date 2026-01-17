package scheduler

import (
	"sort"

	"kclone-go/pkg/models"
	"kclone-go/pkg/state"
)

// ChooseNode selects the best node for a pod using bin-packing
func ChooseNode(nodes []*models.Node, pod *models.Pod) *models.Node {
	var eligible []*models.Node
	for _, node := range nodes {
		if node.Fits(pod.Spec.CPURequest, pod.Spec.MemRequest) {
			eligible = append(eligible, node)
		}
	}

	if len(eligible) == 0 {
		return nil
	}

	// Sort by most allocated (bin-packing), then by largest capacity
	sort.Slice(eligible, func(i, j int) bool {
		allocI := eligible[i].CPUAllocated + eligible[i].MemAllocated
		allocJ := eligible[j].CPUAllocated + eligible[j].MemAllocated
		if allocI != allocJ {
			return allocI < allocJ
		}
		capI := eligible[i].CPUCapacity + eligible[i].MemCapacity
		capJ := eligible[j].CPUCapacity + eligible[j].MemCapacity
		return capI > capJ
	})

	return eligible[0]
}

// SchedulePendingPods attempts to schedule all pending pods
func SchedulePendingPods(cs *state.ClusterState) {
	pods := cs.GetPods()
	nodes := cs.GetNodes()

	for _, pod := range pods {
		if pod.Status.Phase == "Pending" {
			node := ChooseNode(nodes, pod)
			if node != nil {
				cs.BindPod(pod.UID, node.Name)
			} else {
				cs.SetPodFailed(pod.UID, "No nodes have enough free resources")
			}
		}
	}
}
