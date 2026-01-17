from __future__ import annotations

from typing import Dict, List

from .models import Deployment, Node, Pod, PodSpec, Service


class ClusterState:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.pods: Dict[str, Pod] = {}
        self.services: Dict[str, Service] = {}
        self.deployments: Dict[str, Deployment] = {}
        self._uid_counter: int = 0
        self._vip_counter: int = 1

    def _next_uid(self) -> str:
        self._uid_counter += 1
        return f"pod-{self._uid_counter}"

    def add_node(self, node: Node) -> None:
        if node.name in self.nodes:
            raise ValueError(f"Node {node.name} already exists")
        self.nodes[node.name] = node

    def restore_counters(self, uid_counter: int, vip_counter: int) -> None:
        self._uid_counter = uid_counter
        self._vip_counter = vip_counter

    def add_pod(self, spec: PodSpec) -> Pod:
        uid = self._next_uid()
        pod = Pod(name=spec.name, spec=spec, uid=uid)
        self.pods[uid] = pod
        return pod

    def remove_pod(self, uid: str) -> None:
        pod = self.pods.pop(uid, None)
        if not pod:
            raise KeyError(f"Pod {uid} not found")
        if pod.status.node_name:
            node = self.nodes.get(pod.status.node_name)
            if node:
                node.cpu_allocated = max(0, node.cpu_allocated - pod.spec.cpu_request)
                node.mem_allocated = max(0, node.mem_allocated - pod.spec.mem_request)

    def bind_pod(self, uid: str, node_name: str) -> None:
        pod = self.pods[uid]
        node = self.nodes[node_name]
        if not node.fits(pod.spec.cpu_request, pod.spec.mem_request):
            raise ValueError(f"Node {node_name} lacks resources for pod {uid}")
        node.cpu_allocated += pod.spec.cpu_request
        node.mem_allocated += pod.spec.mem_request
        pod.status.node_name = node_name
        pod.status.phase = "Running"

    def set_pod_failed(self, uid: str, message: str) -> None:
        pod = self.pods[uid]
        pod.status.phase = "Failed"
        pod.status.message = message

    def add_service(self, service: Service) -> None:
        if service.name in self.services:
            raise ValueError(f"Service {service.name} already exists")
        self.services[service.name] = service

    def allocate_virtual_ip(self) -> str:
        vip = f"10.96.0.{self._vip_counter}"
        self._vip_counter += 1
        return vip

    def add_deployment(self, deployment: Deployment) -> None:
        if deployment.name in self.deployments:
            raise ValueError(f"Deployment {deployment.name} already exists")
        self.deployments[deployment.name] = deployment

    def select_pods(self, selector: Dict[str, str]) -> List[Pod]:
        def matches(pod: Pod) -> bool:
            return all(pod.spec.labels.get(k) == v for k, v in selector.items())

        return [pod for pod in self.pods.values() if matches(pod)]

    def refresh_service_endpoints(self) -> None:
        for service in self.services.values():
            matched = self.select_pods(service.selector)
            service.endpoints = [pod.uid for pod in matched if pod.status.phase == "Running"]
