package controllers

import (
	"fmt"
	"kclone-go/pkg/models"
	"kclone-go/pkg/scheduler"
	"kclone-go/pkg/state"
)

// CreateDeployment creates a new deployment
func CreateDeployment(cs *state.ClusterState, deployment *models.Deployment) error {
	return cs.AddDeployment(deployment)
}

// ReconcileDeployments ensures all deployments have the correct number of replicas
func ReconcileDeployments(cs *state.ClusterState) {
	deployments := cs.GetDeployments()

	for _, deploy := range deployments {
		matching := cs.SelectPods(deploy.Selector)

		// Count active pods
		var active []*models.Pod
		for _, pod := range matching {
			if pod.Status.Phase == "Pending" || pod.Status.Phase == "Running" {
				active = append(active, pod)
			}
		}

		diff := deploy.Replicas - len(active)

		if diff > 0 {
			// Create missing pods
			for i := 0; i < diff; i++ {
				podName := getPodName(deploy.Name, len(active)+i+1)
				spec := models.PodSpec{
					Name:       podName,
					Image:      deploy.Image,
					CPURequest: deploy.CPURequest,
					MemRequest: deploy.MemRequest,
					Labels:     copyMap(deploy.Labels),
				}
				cs.AddPod(spec)
			}
		} else if diff < 0 {
			// Remove excess pods
			excess := active[len(active)+diff:]
			for _, pod := range excess {
				cs.RemovePod(pod.UID)
			}
		}
	}

	scheduler.SchedulePendingPods(cs)
	cs.RefreshServiceEndpoints()
}

func getPodName(deployName string, index int) string {
	return fmt.Sprintf("%s-%d", deployName, index)
}

func copyMap(m map[string]string) map[string]string {
	result := make(map[string]string)
	for k, v := range m {
		result[k] = v
	}
	return result
}
