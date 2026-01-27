from __future__ import annotations

from .models import Service
from .state import ClusterState


def create_service(state: ClusterState, name: str, selector: dict, port: int, target_port: int) -> Service:
    vip = state.allocate_virtual_ip()
    svc = Service(name=name, selector=selector, port=port, target_port=target_port, virtual_ip=vip)
    state.add_service(svc)
    state.refresh_service_endpoints()
    return svc


def route_request(state: ClusterState, service_name: str) -> str:
    # Refresh endpoints before routing
    state.refresh_service_endpoints()
    svc = state.services.get(service_name)
    if not svc:
        raise KeyError(f"Service {service_name} not found")
    if not svc.endpoints:
        raise RuntimeError(f"Service {service_name} has no ready pods")
    pod_uid = svc.endpoints[svc.rr_index % len(svc.endpoints)]
    svc.rr_index = (svc.rr_index + 1) % len(svc.endpoints)
    return pod_uid
