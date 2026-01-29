from __future__ import annotations

from typing import Dict, List, Optional
from threading import RLock
import subprocess
import threading
import time
import sys
import os
import signal
import psutil

from .models import Deployment, Node, Pod, PodSpec, Service


class ClusterState:
    """Thread-safe in-memory cluster state for K-Clone (Python).

    Provides basic operations for nodes, pods, services and deployments.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self.nodes: Dict[str, Node] = {}
        self.pods: Dict[str, Pod] = {}
        self.services: Dict[str, Service] = {}
        self.deployments: Dict[str, Deployment] = {}
        self._uid_counter: int = 0
        self._vip_counter: int = 1
        # map pod uid -> subprocess.Popen for running pod processes
        self._processes: Dict[str, subprocess.Popen] = {}

        # start background monitor thread
        self._monitor_stop = False
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _next_uid(self) -> str:
        with self._lock:
            self._uid_counter += 1
            return f"pod-{self._uid_counter}"

    def add_node(self, node: Node) -> None:
        with self._lock:
            if node.name in self.nodes:
                raise ValueError(f"Node {node.name} already exists")
            self.nodes[node.name] = node

    def get_node(self, name: str) -> Optional[Node]:
        with self._lock:
            return self.nodes.get(name)

    def add_pod(self, spec: PodSpec) -> Pod:
        with self._lock:
            uid = self._next_uid()
            pod = Pod(name=spec.name, spec=spec, uid=uid)
            self.pods[uid] = pod
            return pod

    def get_pod(self, uid: str) -> Optional[Pod]:
        with self._lock:
            return self.pods.get(uid)

    def remove_pod(self, uid: str) -> None:
        with self._lock:
            pod = self.pods.pop(uid, None)
            if not pod:
                raise KeyError(f"Pod {uid} not found")
            if pod.status.node_name:
                node = self.nodes.get(pod.status.node_name)
                if node:
                    node.cpu_allocated = max(0, node.cpu_allocated - pod.spec.cpu_request)
                    node.mem_allocated = max(0, node.mem_allocated - pod.spec.mem_request)
            # ensure any running subprocess is stopped
            proc = self._processes.pop(uid, None)
            if proc:
                try:
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                except Exception:
                    pass

    def bind_pod(self, uid: str, node_name: str) -> None:
        with self._lock:
            pod = self.pods.get(uid)
            if not pod:
                raise KeyError(f"Pod {uid} not found")
            node = self.nodes.get(node_name)
            if not node:
                raise KeyError(f"Node {node_name} not found")
            if not node.fits(pod.spec.cpu_request, pod.spec.mem_request):
                raise ValueError(f"Node {node_name} lacks resources for pod {uid}")
            node.cpu_allocated += pod.spec.cpu_request
            node.mem_allocated += pod.spec.mem_request
            pod.status.node_name = node_name
            pod.mark_running()
            # start a subprocess that simulates the pod workload
            proc = self._start_pod_process(uid, pod.spec.image)
            if proc:
                self._processes[uid] = proc
                pod.pid = proc.pid

    def mark_pod_failed(self, uid: str, message: str) -> None:
        with self._lock:
            pod = self.pods.get(uid)
            if not pod:
                raise KeyError(f"Pod {uid} not found")
            pod.mark_failed(message)

    def add_service(self, service: Service) -> None:
        with self._lock:
            if service.name in self.services:
                raise ValueError(f"Service {service.name} already exists")
            self.services[service.name] = service

    def allocate_virtual_ip(self) -> str:
        with self._lock:
            vip = f"10.96.0.{self._vip_counter}"
            self._vip_counter += 1
            return vip

    def _start_pod_process(self, uid: str, image: str) -> Optional[subprocess.Popen]:
        """Spawn a worker subprocess to simulate the pod workload.

        The subprocess runs the package module `kclone.worker` so it is available
        in the same environment and can be monitored by PID and exit code.
        """
        try:
            cmd = [sys.executable, "-m", "kclone.worker", "--uid", uid, "--image", image]
            # detach stdout/stderr so it doesn't block; process will live as long as needed
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return proc
        except Exception:
            return None

    def _monitor_loop(self) -> None:
        """Background loop that monitors subprocesses and restarts pods according
        to their restart policy when they exit unexpectedly.
        """
        while not self._monitor_stop:
            time.sleep(1)
            # snapshot keys to avoid locking for long
            uids = list(self._processes.keys())
            for uid in uids:
                with self._lock:
                    proc = self._processes.get(uid)
                    pod = self.pods.get(uid)
                    if not pod or not proc:
                        continue
                    ret = proc.poll()
                    if ret is None:
                        # still running; optionally gather resource usage
                        try:
                            p = psutil.Process(proc.pid)
                            # we could store metrics on pod.status if desired
                            _cpu = p.cpu_percent(interval=0.0)
                            _mem = p.memory_info().rss
                        except Exception:
                            pass
                        continue
                    # process exited
                    # remove mapping and mark pod failed
                    self._processes.pop(uid, None)
                    pod.pid = None
                    pod.mark_failed(f"process exited with code {ret}")
                    # free node resources
                    if pod.status.node_name:
                        node = self.nodes.get(pod.status.node_name)
                        if node:
                            node.cpu_allocated = max(0, node.cpu_allocated - pod.spec.cpu_request)
                            node.mem_allocated = max(0, node.mem_allocated - pod.spec.mem_request)
                        pod.status.node_name = None
                    # decide on restart
                    policy = (pod.spec.restart_policy or "Always")
                    should_restart = False
                    if policy == "Always":
                        should_restart = True
                    elif policy == "OnFailure" and ret != 0:
                        should_restart = True
                    if should_restart:
                        # create a replacement pod and try to schedule it
                        spec = pod.spec
                        # increment restart count
                        pod.status.restart_count = pod.status.restart_count + 1
                        new_pod = self.add_pod(spec)
                        try:
                            # import scheduler locally to avoid circular import
                            from .scheduler import schedule_pending_pods

                            schedule_pending_pods(self)
                        except Exception:
                            pass

    def add_deployment(self, deployment: Deployment) -> None:
        with self._lock:
            if deployment.name in self.deployments:
                raise ValueError(f"Deployment {deployment.name} already exists")
            self.deployments[deployment.name] = deployment

    def restore_counters(self, uid_counter: int, vip_counter: int) -> None:
        with self._lock:
            self._uid_counter = uid_counter
            self._vip_counter = vip_counter

    def select_pods(self, selector: Dict[str, str]) -> List[Pod]:
        def matches(pod: Pod) -> bool:
            return all(pod.spec.labels.get(k) == v for k, v in selector.items())

        with self._lock:
            return [pod for pod in self.pods.values() if matches(pod)]

    def refresh_service_endpoints(self) -> None:
        with self._lock:
            for service in self.services.values():
                matched = [pod for pod in self.pods.values() if all(pod.spec.labels.get(k) == v for k, v in service.selector.items())]
                service.endpoints = [pod.uid for pod in matched if pod.status.phase == "Running"]

    def list_nodes(self) -> List[Node]:
        with self._lock:
            return list(self.nodes.values())

    def list_pods(self) -> List[Pod]:
        with self._lock:
            return list(self.pods.values())

