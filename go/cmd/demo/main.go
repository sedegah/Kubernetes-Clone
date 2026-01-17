package main

import (
	"fmt"

	"kclone-go/pkg/controllers"
	"kclone-go/pkg/models"
	"kclone-go/pkg/resource"
	"kclone-go/pkg/service"
	"kclone-go/pkg/state"
)

func main() {
	cs := state.NewClusterState()

	// Add nodes
	cs.AddNode(&models.Node{Name: "node-a", CPUCapacity: 4, MemCapacity: 4096})
	cs.AddNode(&models.Node{Name: "node-b", CPUCapacity: 2, MemCapacity: 2048})

	// Create deployment
	deploy := &models.Deployment{
		Name:       "web",
		Image:      "nginx:latest",
		Replicas:   3,
		Selector:   map[string]string{"app": "web"},
		Labels:     map[string]string{"app": "web"},
		CPURequest: 1,
		MemRequest: 128,
	}
	controllers.CreateDeployment(cs, deploy)
	controllers.ReconcileDeployments(cs)

	// Create service
	svc, _ := service.CreateService(cs, "web", map[string]string{"app": "web"}, 80, 80)

	// Display state
	fmt.Println("=== Nodes ===")
	for _, row := range resource.GetNodeResourceTable(cs) {
		fmt.Printf("%s: CPU %d/%d, Mem %d/%d\n",
			row.Name, row.CPUUsed, row.CPUCapacity, row.MemUsed, row.MemCapacity)
	}

	fmt.Println("\n=== Pods ===")
	for _, pod := range cs.GetPods() {
		fmt.Printf("%s: %s on %s (%s)\n", pod.UID, pod.Name, pod.Status.NodeName, pod.Status.Phase)
	}

	fmt.Println("\n=== Service ===")
	fmt.Printf("%s: VIP %s, Endpoints: %v\n", svc.Name, svc.VirtualIP, svc.Endpoints)

	fmt.Println("\n=== Routes ===")
	for i := 0; i < 3; i++ {
		podUID, _ := service.RouteRequest(cs, "web")
		fmt.Printf("Request %d -> %s\n", i+1, podUID)
	}

	fmt.Println("\n=== Cluster Capacity ===")
	caps := resource.GetClusterCapacity(cs)
	fmt.Printf("CPU: %d/%d, Mem: %d/%d\n", caps.CPUUsed, caps.CPUTotal, caps.MemUsed, caps.MemTotal)
}
