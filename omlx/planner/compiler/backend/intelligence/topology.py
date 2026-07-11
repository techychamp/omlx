# SPDX-License-Identifier: Apache-2.0
"""
Hardware topology models for backend intelligence framework.
"""
from dataclasses import dataclass
import enum
from types import MappingProxyType
from typing import Any

class HardwareTopologyClass(str, enum.Enum):
    SINGLE_DEVICE = "single_device"
    UNIFIED_MEMORY = "unified_memory"
    DISCRETE_GPU = "discrete_gpu"
    MULTI_GPU = "multi_gpu"
    DISTRIBUTED = "distributed"
    REMOTE = "remote"
    NUMA = "numa"

@dataclass(frozen=True)
class HardwareTopology:
    topology_class: HardwareTopologyClass
    node_count: int = 1
    device_count_per_node: int = 1
    has_unified_memory: bool = False
    interconnect_type: str = "pcie"
    interconnect_bandwidth_gbps: float = 0.0
    numa_nodes: int = 1
    topology_metadata: MappingProxyType[str, Any] = MappingProxyType({})
