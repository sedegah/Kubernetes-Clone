from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import Deployment, Node, Pod, PodSpec, PodStatus, Service
from .state import ClusterState


def _state_to_dict(state: ClusterState) -> Dict[str, Any]:
    return {
        "uid_counter": state._uid_counter,  # type: ignore[attr-defined]
        "vip_counter": state._vip_counter,  # type: ignore[attr-defined]
        "nodes": [
            {
                "name": n.name,
                "cpu_capacity": n.cpu_capacity,
                "mem_capacity": n.mem_capacity,
                "labels": n.labels,
                "cpu_allocated": n.cpu_allocated,
                "mem_allocated": n.mem_allocated,
            }
            for n in state.nodes.values()
        ],
        "pods": [
            {
                "uid": p.uid,
                "name": p.name,
                "spec": {
                    "name": p.spec.name,
                    "image": p.spec.image,
                    "cpu_request": p.spec.cpu_request,
                    "mem_request": p.spec.mem_request,
                    "labels": p.spec.labels,
                },
                "status": {
                    "phase": p.status.phase,
                    "node_name": p.status.node_name,
                    "message": p.status.message,
                },
            }
            for p in state.pods.values()
        ],
        "services": [
            {
                "name": s.name,
                "selector": s.selector,
                "port": s.port,
                "target_port": s.target_port,
                "virtual_ip": s.virtual_ip,
                "endpoints": s.endpoints,
                "rr_index": s.rr_index,
            }
            for s in state.services.values()
        ],
        "deployments": [
            {
                "name": d.name,
                "image": d.image,
                "replicas": d.replicas,
                "selector": d.selector,
                "labels": d.labels,
                "cpu_request": d.cpu_request,
                "mem_request": d.mem_request,
            }
            for d in state.deployments.values()
        ],
    }


def _dict_to_state(data: Dict[str, Any]) -> ClusterState:
    state = ClusterState()
    for n in data.get("nodes", []):
        node = Node(
            name=n["name"],
            cpu_capacity=n["cpu_capacity"],
            mem_capacity=n["mem_capacity"],
            labels=n.get("labels", {}),
        )
        node.cpu_allocated = n.get("cpu_allocated", 0)
        node.mem_allocated = n.get("mem_allocated", 0)
        state.add_node(node)

    for p in data.get("pods", []):
        spec_data = p["spec"]
        status_data = p["status"]
        spec = PodSpec(
            name=spec_data["name"],
            image=spec_data["image"],
            cpu_request=spec_data.get("cpu_request", 1),
            mem_request=spec_data.get("mem_request", 128),
            labels=spec_data.get("labels", {}),
        )
        status = PodStatus(
            phase=status_data.get("phase", "Pending"),
            node_name=status_data.get("node_name"),
            message=status_data.get("message", ""),
        )
        pod = Pod(name=p["name"], spec=spec, status=status, uid=p["uid"])
        state.pods[pod.uid] = pod

    for s in data.get("services", []):
        svc = Service(
            name=s["name"],
            selector=s["selector"],
            port=s["port"],
            target_port=s["target_port"],
            virtual_ip=s["virtual_ip"],
            endpoints=s.get("endpoints", []),
        )
        svc.rr_index = s.get("rr_index", 0)
        state.services[svc.name] = svc

    for d in data.get("deployments", []):
        deploy = Deployment(
            name=d["name"],
            image=d["image"],
            replicas=d["replicas"],
            selector=d["selector"],
            labels=d.get("labels", {}),
            cpu_request=d.get("cpu_request", 1),
            mem_request=d.get("mem_request", 128),
        )
        state.deployments[deploy.name] = deploy

    uid_counter = data.get("uid_counter", 0)
    vip_counter = data.get("vip_counter", 1)
    state.restore_counters(uid_counter, vip_counter)
    state.refresh_service_endpoints()
    return state


def save_state(state: ClusterState, path: str | Path) -> None:
    payload = _state_to_dict(state)
    Path(path).write_text(json.dumps(payload, indent=2))


def load_state(path: str | Path) -> ClusterState:
    data = json.loads(Path(path).read_text())
    return _dict_to_state(data)
