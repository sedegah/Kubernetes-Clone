package models

// Node represents a worker node in the cluster
type Node struct {
	Name         string
	CPUCapacity  int
	MemCapacity  int
	Labels       map[string]string
	CPUAllocated int
	MemAllocated int
	Ready        bool
	Taints       []string
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
	Phase        string // Pending, Running, Failed
	NodeName     string
	Message      string
	Healthy      bool
	RestartCount int
	StartTime    string
}

// HealthCheck defines health check configuration
type HealthCheck struct {
	Enabled          bool
	InitialDelaySec  int
	PeriodSec        int
	TimeoutSec       int
	FailureThreshold int
}

// PodSpec defines the desired state of a pod
type PodSpec struct {
	Name          string
	Image         string
	CPURequest    int
	MemRequest    int
	Labels        map[string]string
	HealthCheck   HealthCheck
	RestartPolicy string // Always, OnFailure, Never
}

// Pod represents a scheduled workload
type Pod struct {
	UID    string    `json:"uid"`
	Name   string    `json:"name"`
	Spec   PodSpec   `json:"spec"`
	Status PodStatus `json:"status"`
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

// Pod helper methods
func (p *Pod) MarkRunning() {
	p.Status.Phase = "Running"
}

func (p *Pod) MarkFailed(msg string) {
	p.Status.Phase = "Failed"
	p.Status.Message = msg
}
