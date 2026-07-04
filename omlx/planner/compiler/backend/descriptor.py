# SPDX-License-Identifier: Apache-2.0
"""
Backend Capabilities and Descriptors.
"""
from __future__ import annotations
import enum
import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

class BackendCapability(str, enum.Enum):
    AUTOREGRESSIVE = "supports_autoregressive"
    DIFFUSION = "supports_diffusion"
    MULTIMODAL = "supports_multimodal"
    EXPERT_ROUTING = "supports_expert_routing"
    TRIAGE = "supports_triage"
    SPECULATIVE_DECODING = "supports_speculative_decoding"
    GRAPH_EXECUTION = "supports_graph_execution"
    ASYNC_EXECUTION = "supports_async_execution"
    PAGED_KV_CACHE = "supports_paged_kv_cache"
    SSD_CACHE = "supports_ssd_cache"
    PREFIX_CACHE = "supports_prefix_cache"
    VERIFICATION = "supports_verification"
    DYNAMIC_BATCHING = "supports_dynamic_batching"
    CONTINUOUS_BATCHING = "supports_continuous_batching"
    HETEROGENEOUS_EXECUTION = "supports_heterogeneous_execution"
    DISTRIBUTED_EXECUTION = "supports_distributed_execution"
    RUNTIME_COMPILATION = "supports_runtime_compilation"
    STREAMING = "supports_streaming"
    CUSTOM_SYNCHRONIZATION = "supports_custom_synchronization"

@dataclass(frozen=True)
class BackendDescriptor:
    backend_id: str
    backend_version: str
    backend_family: str
    backend_generation: str
    supported_execution_semantics: tuple[str, ...]
    supported_operation_mappings: tuple[str, ...]
    supported_execution_families: tuple[str, ...]
    supported_cache_layouts: tuple[str, ...]
    supported_synchronization_primitives: tuple[str, ...]
    supported_optimization_capabilities: tuple[str, ...]
    supported_quantization_formats: tuple[str, ...]
    supported_precision_formats: tuple[str, ...]
    supported_cache_strategies: tuple[str, ...]
    supported_execution_modes: tuple[str, ...]
    supported_routing_strategies: tuple[str, ...]
    supported_graph_features: tuple[str, ...]
    hardware_capabilities: tuple[str, ...]
    hardware_metadata: MappingProxyType[str, Any]
    memory_model: str
    memory_topology: str
    execution_topology: str
    stream_model: str
    device_topology: str
    backend_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

class BackendDescriptorRegistry:
    """A locked thread-safe registry of backend descriptors."""
    def __init__(self) -> None:
        self._descriptors: dict[str, BackendDescriptor] = {}
        self._is_locked = False
        self._lock = threading.RLock()

    def register(self, backend_id: str, descriptor: BackendDescriptor) -> None:
        with self._lock:
            if self._is_locked:
                raise RuntimeError("BackendDescriptorRegistry is locked and cannot be modified.")
            if backend_id in self._descriptors:
                raise ValueError(f"Backend descriptor '{backend_id}' is already registered.")
            self._descriptors[backend_id] = descriptor

    def get(self, backend_id: str) -> BackendDescriptor:
        with self._lock:
            if backend_id not in self._descriptors:
                raise KeyError(f"Backend descriptor '{backend_id}' not found.")
            return self._descriptors[backend_id]

    def exists(self, backend_id: str) -> bool:
        with self._lock:
            return backend_id in self._descriptors

    def lock(self) -> None:
        with self._lock:
            self._is_locked = True
