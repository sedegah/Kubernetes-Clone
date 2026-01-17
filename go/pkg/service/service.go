package service

import (
	"fmt"

	"kclone-go/pkg/models"
	"kclone-go/pkg/state"
)

// CreateService creates a new service
func CreateService(cs *state.ClusterState, name string, selector map[string]string, port, targetPort int) (*models.Service, error) {
	vip := cs.AllocateVirtualIP()
	svc := &models.Service{
		Name:       name,
		Selector:   selector,
		Port:       port,
		TargetPort: targetPort,
		VirtualIP:  vip,
		Endpoints:  []string{},
		RRIndex:    0,
	}
	err := cs.AddService(svc)
	if err != nil {
		return nil, err
	}
	cs.RefreshServiceEndpoints()
	return svc, nil
}

// RouteRequest performs round-robin routing to a pod
func RouteRequest(cs *state.ClusterState, serviceName string) (string, error) {
	svc, exists := cs.GetService(serviceName)
	if !exists {
		return "", fmt.Errorf("service %s not found", serviceName)
	}

	cs.RefreshServiceEndpoints()

	if len(svc.Endpoints) == 0 {
		return "", fmt.Errorf("service %s has no ready pods", serviceName)
	}

	podUID := svc.Endpoints[svc.RRIndex%len(svc.Endpoints)]
	svc.RRIndex = (svc.RRIndex + 1) % len(svc.Endpoints)

	return podUID, nil
}
