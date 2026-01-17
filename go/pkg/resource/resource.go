package resource

import (
	"kclone-go/pkg/state"
)

// NodeResourceInfo represents resource info for a node
type NodeResourceInfo struct {
	Name        string
	CPUUsed     int
	CPUCapacity int
	MemUsed     int
	MemCapacity int
}

// ClusterCapacity represents total cluster resources
type ClusterCapacity struct {
	CPUUsed  int
	CPUTotal int
	MemUsed  int
	MemTotal int
}

// GetNodeResourceTable returns resource info for all nodes
func GetNodeResourceTable(cs *state.ClusterState) []NodeResourceInfo {
	nodes := cs.GetNodes()
	result := make([]NodeResourceInfo, 0, len(nodes))

	for _, node := range nodes {
		result = append(result, NodeResourceInfo{
			Name:        node.Name,
			CPUUsed:     node.CPUAllocated,
			CPUCapacity: node.CPUCapacity,
			MemUsed:     node.MemAllocated,
			MemCapacity: node.MemCapacity,
		})
	}

	return result
}

// GetClusterCapacity returns total cluster resource usage
func GetClusterCapacity(cs *state.ClusterState) ClusterCapacity {
	nodes := cs.GetNodes()

	capacity := ClusterCapacity{}
	for _, node := range nodes {
		capacity.CPUTotal += node.CPUCapacity
		capacity.MemTotal += node.MemCapacity
		capacity.CPUUsed += node.CPUAllocated
		capacity.MemUsed += node.MemAllocated
	}

	return capacity
}
