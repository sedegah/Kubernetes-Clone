from __future__ import annotations

from typing import Dict, List

from .state import ClusterState


def node_resource_table(state: ClusterState) -> List[Dict[str, int]]:
    rows = []
    for node in state.nodes.values():
        rows.append(
            {
                "name": node.name,
                "cpu_used": node.cpu_allocated,
                "cpu_capacity": node.cpu_capacity,
                "mem_used": node.mem_allocated,
                "mem_capacity": node.mem_capacity,
            }
        )
    return rows


def cluster_capacity(state: ClusterState) -> Dict[str, int]:
    total_cpu = sum(n.cpu_capacity for n in state.nodes.values())
    total_mem = sum(n.mem_capacity for n in state.nodes.values())
    used_cpu = sum(n.cpu_allocated for n in state.nodes.values())
    used_mem = sum(n.mem_allocated for n in state.nodes.values())
    return {
        "cpu_used": used_cpu,
        "cpu_total": total_cpu,
        "mem_used": used_mem,
        "mem_total": total_mem,
    }
