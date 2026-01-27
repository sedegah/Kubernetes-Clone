from __future__ import annotations

from typing import List, Optional

from .models import Node, Pod
from .state import ClusterState


def choose_node(nodes: List[Node], pod: Pod) -> Optional[Node]:
    """Select the best node for a pod using a least-requested scoring strategy.

    Returns the node with the highest available resources that fits the pod.
    """
    eligible: List[Node] = []
    for n in nodes:
        if not n.ready:
            continue
        if n.taints:
            continue
        if n.fits(pod.spec.cpu_request, pod.spec.mem_request):
            eligible.append(n)

    if not eligible:
        return None

    # Score nodes by available CPU and memory (higher is better)
    def score(n: Node) -> int:
        return n.cpu_available * 1000 + n.mem_available

    best = max(eligible, key=score)
    return best


def schedule_pending_pods(state: ClusterState) -> None:
    """Attempt to schedule all pending pods in the cluster state."""
    pending = [p for p in state.list_pods() if p.status.phase == "Pending"]
    for pod in pending:
        node = choose_node(state.list_nodes(), pod)
        if node:
            try:
                state.bind_pod(pod.uid, node.name)
            except Exception as e:
                # mark failed but leave for controller to retry
                state.mark_pod_failed(pod.uid, str(e))
        else:
            # leave as Pending so controller/scheduler can retry later
            continue
