from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time


@dataclass
class Node:
    name: str
    cpu_capacity: int
    mem_capacity: int
    labels: Dict[str, str] = field(default_factory=dict)
    cpu_allocated: int = 0
    mem_allocated: int = 0
    ready: bool = True
    taints: List[str] = field(default_factory=list)

    @property
    def cpu_available(self) -> int:
        return max(0, self.cpu_capacity - self.cpu_allocated)

    @property
    def mem_available(self) -> int:
        return max(0, self.mem_capacity - self.mem_allocated)

    def fits(self, cpu: int, mem: int) -> bool:
        return cpu <= self.cpu_available and mem <= self.mem_available


@dataclass
class PodStatus:
    phase: str = "Pending"
    node_name: Optional[str] = None
    message: str = ""
    healthy: bool = True
    restart_count: int = 0
    start_time: Optional[float] = None


@dataclass
class HealthCheck:
    enabled: bool = False
    initial_delay_sec: int = 0
    period_sec: int = 10
    timeout_sec: int = 1
    failure_threshold: int = 3


@dataclass
class PodSpec:
    name: str
    image: str
    cpu_request: int = 1
    mem_request: int = 128
    labels: Dict[str, str] = field(default_factory=dict)
    health_check: HealthCheck = field(default_factory=HealthCheck)
    restart_policy: str = "Always"  # Always, OnFailure, Never


@dataclass
class Pod:
    name: str
    spec: PodSpec
    status: PodStatus = field(default_factory=PodStatus)
    uid: str = ""

    def mark_running(self) -> None:
        self.status.phase = "Running"
        self.status.start_time = time.time()

    def mark_failed(self, msg: str) -> None:
        self.status.phase = "Failed"
        self.status.message = msg

    def mark_pending(self) -> None:
        self.status.phase = "Pending"


@dataclass
class Service:
    name: str
    selector: Dict[str, str]
    port: int
    target_port: int
    virtual_ip: str
    endpoints: List[str] = field(default_factory=list)  # list of pod uids
    rr_index: int = 0


@dataclass
class Deployment:
    name: str
    image: str
    replicas: int
    selector: Dict[str, str]
    labels: Dict[str, str] = field(default_factory=dict)
    cpu_request: int = 1
    mem_request: int = 128
 