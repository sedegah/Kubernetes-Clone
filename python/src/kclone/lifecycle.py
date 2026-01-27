from __future__ import annotations

from datetime import datetime
from typing import Dict

from .models import PodSpec
from .scheduler import schedule_pending_pods
from .state import ClusterState


def create_pod(
    state: ClusterState,
    name: str,
    image: str,
    cpu_request: int,
    mem_request: int,
    labels: Dict[str, str],
) -> None:
    spec = PodSpec(name=name, image=image, cpu_request=cpu_request, mem_request=mem_request, labels=labels)
    pod = state.add_pod(spec)
    # trigger scheduling attempt
    schedule_pending_pods(state)
    state.refresh_service_endpoints()
    return pod


def delete_pod(state: ClusterState, uid: str) -> None:
    state.remove_pod(uid)
    state.refresh_service_endpoints()


def health_check_pod(state: ClusterState, uid: str) -> bool:
    """Perform a basic health check simulation for a pod."""
    pod = state.get_pod(uid)
    if not pod:
        raise KeyError(f"Pod {uid} not found")
    if pod.status.phase == "Running":
        pod.status.healthy = True
        pod.status.start_time = datetime.now().timestamp()
        return True
    return False


def restart_pod(state: ClusterState, uid: str) -> None:
    """Restart a pod according to its restart policy."""
    pod = state.get_pod(uid)
    if not pod:
        raise KeyError(f"Pod {uid} not found")

    if pod.spec.restart_policy == "Never":
        raise ValueError(f"Pod {uid} has restart policy Never")

    spec = pod.spec
    restart_count = pod.status.restart_count

    # delete and create new
    delete_pod(state, uid)
    new_pod = state.add_pod(spec)
    new_pod.status.restart_count = restart_count + 1
    schedule_pending_pods(state)
    state.refresh_service_endpoints()
