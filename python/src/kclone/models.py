from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Node:
    name: str
    cpu_capacity: int
    mem_capacity: int
    labels: Dict[str, str] = field(default_factory=dict)
    cpu_allocated: int = 0
    mem_allocated: int = 0

    @property
    def cpu_available(self) -> int:
        return self.cpu_capacity - self.cpu_allocated

    @property
    def mem_available(self) -> int:
        return self.mem_capacity - self.mem_allocated

    def fits(self, cpu: int, mem: int) -> bool:
        return cpu <= self.cpu_available and mem <= self.mem_available


@dataclass
class PodStatus:
    phase: str = "Pending"
    node_name: Optional[str] = None
    message: str = ""


@dataclass
class PodSpec:
    name: str
    image: str
    cpu_request: int = 1
    mem_request: int = 128
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Pod:
    name: str
    spec: PodSpec
    status: PodStatus = field(default_factory=PodStatus)
    uid: str = ""


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
