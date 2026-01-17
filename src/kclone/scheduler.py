from __future__ import annotations

from typing import List, Optional

from .models import Node, Pod
from .state import ClusterState


def choose_node(nodes: List[Node], pod: Pod) -> Optional[Node]:
    eligible = [n for n in nodes if n.fits(pod.spec.cpu_request, pod.spec.mem_request)]
    if not eligible:
        return None
    eligible.sort(key=lambda n: (n.cpu_allocated + n.mem_allocated, -n.cpu_capacity - n.mem_capacity))
    return eligible[0]


def schedule_pending_pods(state: ClusterState) -> None:
    pending = [p for p in state.pods.values() if p.status.phase == "Pending"]
    for pod in pending:
        node = choose_node(list(state.nodes.values()), pod)
        if node:
            state.bind_pod(pod.uid, node.name)
        else:
            state.set_pod_failed(pod.uid, "No nodes have enough free resources")
