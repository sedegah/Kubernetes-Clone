from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import Deployment, HealthCheck, Node, Pod, PodSpec, PodStatus, Service
from .state import ClusterState
from . import db as _db


def _state_to_dict(state: ClusterState) -> Dict[str, Any]:
    return {
        "uid_counter": getattr(state, "_uid_counter", 0),
        "vip_counter": getattr(state, "_vip_counter", 1),
        "nodes": [
            {
                "name": n.name,
                "cpu_capacity": n.cpu_capacity,
                "mem_capacity": n.mem_capacity,
                "labels": n.labels,
                "cpu_allocated": n.cpu_allocated,
                "mem_allocated": n.mem_allocated,
                "ready": n.ready,
                "taints": n.taints,
            }
            for n in state.list_nodes()
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
                    "restart_policy": p.spec.restart_policy,
                    "health_check": {
                        "enabled": p.spec.health_check.enabled,
                        "initial_delay_sec": p.spec.health_check.initial_delay_sec,
                        "period_sec": p.spec.health_check.period_sec,
                        "timeout_sec": p.spec.health_check.timeout_sec,
                        "failure_threshold": p.spec.health_check.failure_threshold,
                    },
                },
                "status": {
                    "phase": p.status.phase,
                    "node_name": p.status.node_name,
                    "message": p.status.message,
                    "healthy": p.status.healthy,
                    "restart_count": p.status.restart_count,
                    "start_time": p.status.start_time,
                },
            }
            for p in state.list_pods()
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
            ready=n.get("ready", True),
            taints=n.get("taints", []),
        )
        node.cpu_allocated = n.get("cpu_allocated", 0)
        node.mem_allocated = n.get("mem_allocated", 0)
        state.add_node(node)

    for p in data.get("pods", []):
        spec_data = p["spec"]
        status_data = p["status"]
        
        hc_data = spec_data.get("health_check", {})
        health_check = HealthCheck(
            enabled=hc_data.get("enabled", False),
            initial_delay_sec=hc_data.get("initial_delay_sec", 0),
            period_sec=hc_data.get("period_sec", 10),
            timeout_sec=hc_data.get("timeout_sec", 1),
            failure_threshold=hc_data.get("failure_threshold", 3),
        )
        
        spec = PodSpec(
            name=spec_data["name"],
            image=spec_data["image"],
            cpu_request=spec_data.get("cpu_request", 1),
            mem_request=spec_data.get("mem_request", 128),
            labels=spec_data.get("labels", {}),
            health_check=health_check,
            restart_policy=spec_data.get("restart_policy", "Always"),
        )
        status = PodStatus(
            phase=status_data.get("phase", "Pending"),
            node_name=status_data.get("node_name"),
            message=status_data.get("message", ""),
            healthy=status_data.get("healthy", True),
            restart_count=status_data.get("restart_count", 0),
            start_time=status_data.get("start_time"),
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
    # Use DB store when path ends with .db; otherwise export JSON
    p = str(path)
    if p.endswith('.db'):
        _db.save_state_to_db(state, path)
        return
    payload = _state_to_dict(state)
    Path(path).write_text(json.dumps(payload, indent=2))


def load_state(path: str | Path) -> ClusterState:
    p = str(path)
    if p.endswith('.db'):
        return _db.load_state_from_db(path)
    data = json.loads(Path(path).read_text())
    return _dict_to_state(data)
