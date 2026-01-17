from __future__ import annotations

from typing import Dict

from .models import Deployment, PodSpec
from .scheduler import schedule_pending_pods
from .state import ClusterState


def create_deployment(
    state: ClusterState,
    name: str,
    image: str,
    replicas: int,
    selector: Dict[str, str],
    labels: Dict[str, str],
    cpu_request: int,
    mem_request: int,
) -> Deployment:
    deploy = Deployment(
        name=name,
        image=image,
        replicas=replicas,
        selector=selector,
        labels=labels,
        cpu_request=cpu_request,
        mem_request=mem_request,
    )
    state.add_deployment(deploy)
    return deploy


def reconcile_deployments(state: ClusterState) -> None:
    for deploy in state.deployments.values():
        matching = state.select_pods(deploy.selector)
        active = [p for p in matching if p.status.phase in ("Pending", "Running")]
        diff = deploy.replicas - len(active)
        if diff > 0:
            for i in range(diff):
                pod_name = f"{deploy.name}-{len(active) + i + 1}"
                labels = {**deploy.labels}
                spec = PodSpec(
                    name=pod_name,
                    image=deploy.image,
                    cpu_request=deploy.cpu_request,
                    mem_request=deploy.mem_request,
                    labels=labels,
                )
                state.add_pod(spec)
        elif diff < 0:
            excess = active[diff:]
            for pod in excess:
                state.remove_pod(pod.uid)
        schedule_pending_pods(state)
    state.refresh_service_endpoints()
