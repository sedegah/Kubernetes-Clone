from __future__ import annotations

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
):
    spec = PodSpec(name=name, image=image, cpu_request=cpu_request, mem_request=mem_request, labels=labels)
    pod = state.add_pod(spec)
    schedule_pending_pods(state)
    state.refresh_service_endpoints()
    return pod


def delete_pod(state: ClusterState, uid: str) -> None:
    state.remove_pod(uid)
    state.refresh_service_endpoints()
