package state

import (
	"encoding/json"
	"fmt"
	"sync"

	"kclone-go/pkg/models"
)

// ClusterState holds all cluster resources
type ClusterState struct {
	mu          sync.RWMutex
	Nodes       map[string]*models.Node
	Pods        map[string]*models.Pod
	Services    map[string]*models.Service
	Deployments map[string]*models.Deployment
	UIDCounter  int `json:"uidCounter"`
	VIPCounter  int `json:"vipCounter"`
}

// NewClusterState creates a new cluster state
func NewClusterState() *ClusterState {
	return &ClusterState{
		Nodes:       make(map[string]*models.Node),
		Pods:        make(map[string]*models.Pod),
		Services:    make(map[string]*models.Service),
		Deployments: make(map[string]*models.Deployment),
		UIDCounter:  0,
		VIPCounter:  1,
	}
}

// AddNode adds a node to the cluster
func (cs *ClusterState) AddNode(node *models.Node) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	if _, exists := cs.Nodes[node.Name]; exists {
		return fmt.Errorf("node %s already exists", node.Name)
	}
	cs.Nodes[node.Name] = node
	return nil
}

// AddPod creates and adds a pod
func (cs *ClusterState) AddPod(spec models.PodSpec) *models.Pod {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	cs.UIDCounter++
	uid := fmt.Sprintf("pod-%d", cs.UIDCounter)
	pod := &models.Pod{
		UID:  uid,
		Name: spec.Name,
		Spec: spec,
		Status: models.PodStatus{
			Phase: "Pending",
		},
	}
	cs.Pods[uid] = pod
	return pod
}

// RemovePod removes a pod and frees resources
func (cs *ClusterState) RemovePod(uid string) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	pod, exists := cs.Pods[uid]
	if !exists {
		return fmt.Errorf("pod %s not found", uid)
	}

	if pod.Status.NodeName != "" {
		if node, ok := cs.Nodes[pod.Status.NodeName]; ok {
			node.CPUAllocated -= pod.Spec.CPURequest
			node.MemAllocated -= pod.Spec.MemRequest
			if node.CPUAllocated < 0 {
				node.CPUAllocated = 0
			}
			if node.MemAllocated < 0 {
				node.MemAllocated = 0
			}
		}
	}

	delete(cs.Pods, uid)
	return nil
}

// BindPod assigns a pod to a node
func (cs *ClusterState) BindPod(uid, nodeName string) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	pod, exists := cs.Pods[uid]
	if !exists {
		return fmt.Errorf("pod %s not found", uid)
	}

	node, exists := cs.Nodes[nodeName]
	if !exists {
		return fmt.Errorf("node %s not found", nodeName)
	}

	if !node.Fits(pod.Spec.CPURequest, pod.Spec.MemRequest) {
		return fmt.Errorf("node %s lacks resources for pod %s", nodeName, uid)
	}

	node.CPUAllocated += pod.Spec.CPURequest
	node.MemAllocated += pod.Spec.MemRequest
	pod.Status.NodeName = nodeName
	pod.Status.Phase = "Running"
	return nil
}

// SetPodFailed marks a pod as failed
func (cs *ClusterState) SetPodFailed(uid, message string) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	pod, exists := cs.Pods[uid]
	if !exists {
		return fmt.Errorf("pod %s not found", uid)
	}

	pod.Status.Phase = "Failed"
	pod.Status.Message = message
	return nil
}

// AddService adds a service
func (cs *ClusterState) AddService(service *models.Service) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	if _, exists := cs.Services[service.Name]; exists {
		return fmt.Errorf("service %s already exists", service.Name)
	}
	cs.Services[service.Name] = service
	return nil
}

// AddDeployment adds a deployment
func (cs *ClusterState) AddDeployment(deployment *models.Deployment) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	if _, exists := cs.Deployments[deployment.Name]; exists {
		return fmt.Errorf("deployment %s already exists", deployment.Name)
	}
	cs.Deployments[deployment.Name] = deployment
	return nil
}

// SelectPods returns pods matching a selector
func (cs *ClusterState) SelectPods(selector map[string]string) []*models.Pod {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	var matched []*models.Pod
	for _, pod := range cs.Pods {
		if matchesSelector(pod.Spec.Labels, selector) {
			matched = append(matched, pod)
		}
	}
	return matched
}

// RefreshServiceEndpoints updates all service endpoints
func (cs *ClusterState) RefreshServiceEndpoints() {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	for _, service := range cs.Services {
		var endpoints []string
		for _, pod := range cs.Pods {
			if matchesSelector(pod.Spec.Labels, service.Selector) && pod.Status.Phase == "Running" {
				endpoints = append(endpoints, pod.UID)
			}
		}
		service.Endpoints = endpoints
	}
}

// AllocateVirtualIP generates a new virtual IP
func (cs *ClusterState) AllocateVirtualIP() string {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	vip := fmt.Sprintf("10.96.0.%d", cs.VIPCounter)
	cs.VIPCounter++
	return vip
}

// GetNodes returns all nodes (safe copy)
func (cs *ClusterState) GetNodes() []*models.Node {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	nodes := make([]*models.Node, 0, len(cs.Nodes))
	for _, node := range cs.Nodes {
		nodes = append(nodes, node)
	}
	return nodes
}

// GetPods returns all pods (safe copy)
func (cs *ClusterState) GetPods() []*models.Pod {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	pods := make([]*models.Pod, 0, len(cs.Pods))
	for _, pod := range cs.Pods {
		pods = append(pods, pod)
	}
	return pods
}

// GetServices returns all services (safe copy)
func (cs *ClusterState) GetServices() []*models.Service {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	services := make([]*models.Service, 0, len(cs.Services))
	for _, svc := range cs.Services {
		services = append(services, svc)
	}
	return services
}

// GetDeployments returns all deployments (safe copy)
func (cs *ClusterState) GetDeployments() []*models.Deployment {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	deploys := make([]*models.Deployment, 0, len(cs.Deployments))
	for _, deploy := range cs.Deployments {
		deploys = append(deploys, deploy)
	}
	return deploys
}

// GetDeployment returns a deployment by name
func (cs *ClusterState) GetDeployment(name string) (*models.Deployment, bool) {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	deploy, exists := cs.Deployments[name]
	return deploy, exists
}

// GetService returns a service by name
func (cs *ClusterState) GetService(name string) (*models.Service, bool) {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	svc, exists := cs.Services[name]
	return svc, exists
}

// RemoveNode removes a node from the cluster and unschedules any pods bound to it.
func (cs *ClusterState) RemoveNode(name string) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	if _, exists := cs.Nodes[name]; !exists {
		return fmt.Errorf("node %s not found", name)
	}

	// Remove the node
	delete(cs.Nodes, name)

	// For any pods that were scheduled on this node, mark them Pending and clear node assignment
	for _, pod := range cs.Pods {
		if pod.Status.NodeName == name {
			pod.Status.NodeName = ""
			pod.Status.Phase = "Pending"
		}
	}

	return nil
}

func matchesSelector(labels, selector map[string]string) bool {
	for k, v := range selector {
		if labels[k] != v {
			return false
		}
	}
	return true
}

// ToJSON serializes cluster state to JSON
func (cs *ClusterState) ToJSON() []byte {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	data, _ := json.MarshalIndent(cs, "", "  ")
	return data
}

// FromJSON deserializes cluster state from JSON
func (cs *ClusterState) FromJSON(data []byte) error {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	return json.Unmarshal(data, cs)
}
