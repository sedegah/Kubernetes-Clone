package models

// Node represents a worker node in the cluster
type Node struct {
	Name         string
	CPUCapacity  int
	MemCapacity  int
	Labels       map[string]string
	CPUAllocated int
	MemAllocated int
}

// CPUAvailable returns available CPU
func (n *Node) CPUAvailable() int {
	return n.CPUCapacity - n.CPUAllocated
}

// MemAvailable returns available memory
func (n *Node) MemAvailable() int {
	return n.MemCapacity - n.MemAllocated
}

// Fits checks if a pod fits on this node
func (n *Node) Fits(cpuRequest, memRequest int) bool {
	return cpuRequest <= n.CPUAvailable() && memRequest <= n.MemAvailable()
}

// PodStatus represents the current state of a pod
type PodStatus struct {
	Phase    string // Pending, Running, Failed
	NodeName string
	Message  string
}

// PodSpec defines the desired state of a pod
type PodSpec struct {
	Name       string
	Image      string
	CPURequest int
	MemRequest int
	Labels     map[string]string
}

// Pod represents a scheduled workload
type Pod struct {
	UID    string
	Name   string
	Spec   PodSpec
	Status PodStatus
}

// Service represents a network endpoint abstraction
type Service struct {
	Name       string
	Selector   map[string]string
	Port       int
	TargetPort int
	VirtualIP  string
	Endpoints  []string // pod UIDs
	RRIndex    int      // round-robin counter
}

// Deployment represents a replica controller
type Deployment struct {
	Name       string
	Image      string
	Replicas   int
	Selector   map[string]string
	Labels     map[string]string
	CPURequest int
	MemRequest int
}
