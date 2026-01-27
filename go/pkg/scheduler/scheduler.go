package scheduler

import (
	"kclone-go/pkg/models"
	"kclone-go/pkg/state"
)

// ChooseNode selects the best node for a pod using bin-packing
func ChooseNode(nodes []*models.Node, pod *models.Pod) *models.Node {
	var eligible []*models.Node
	for _, node := range nodes {
		// Skip nodes that are not ready
		if !node.Ready {
			continue
		}
		// Skip tainted nodes (simplified - in real K8s, pods can have tolerations)
		if len(node.Taints) > 0 {
			continue
		}
		if node.Fits(pod.Spec.CPURequest, pod.Spec.MemRequest) {
			eligible = append(eligible, node)
		}
	}

	if len(eligible) == 0 {
		return nil
	}

	// Score nodes by available CPU and memory (higher score preferred)
	best := eligible[0]
	bestScore := best.CPUAvailable()*1000 + best.MemAvailable()
	for _, n := range eligible[1:] {
		score := n.CPUAvailable()*1000 + n.MemAvailable()
		if score > bestScore {
			best = n
			bestScore = score
		}
	}
	return best
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
