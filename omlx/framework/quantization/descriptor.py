# SPDX-License-Identifier: Apache-2.0
"""
Immutable Quantization Descriptor.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple, Optional
from .types import QuantizationFamily, ValidationStatus, PerformanceClass

@dataclass(frozen=True)
class QuantizationDescriptor:
    """
    Immutable canonical representation of a quantization config.
    """
    quantization_family: QuantizationFamily = QuantizationFamily.UNKNOWN
    storage_precision: str = ""
    compute_precision: str = ""
    weight_precision: str = ""
    activation_precision: str = ""
    kv_cache_precision: str = ""
    group_size: Optional[int] = None
    block_size: Optional[int] = None
    mixed_precision: bool = False
    dynamic_quantization: bool = False
    static_quantization: bool = False
    per_channel: bool = False
    per_group: bool = False
    supports_streaming: bool = False
    supports_batching: bool = False
    supports_speculative_decoding: bool = False
    supported_backends: Tuple[str, ...] = field(default_factory=tuple)
    supported_model_families: Tuple[str, ...] = field(default_factory=tuple)
    packing_information: Optional[str] = None
    layout_information: Optional[str] = None
    alignment_information: Optional[str] = None
    compression_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    compression_ratio: Optional[float] = None
    estimated_memory_usage: Optional[int] = None
    estimated_bandwidth_usage: Optional[int] = None
    required_kernels: Tuple[str, ...] = field(default_factory=tuple)
    hardware_requirements: Tuple[str, ...] = field(default_factory=tuple)
    recommended_backend: Optional[str] = None
    recommended_hardware: Tuple[str, ...] = field(default_factory=tuple)
    conversion_compatibility: Tuple[str, ...] = field(default_factory=tuple)
    performance_class: PerformanceClass = PerformanceClass.UNKNOWN
    validation_status: ValidationStatus = ValidationStatus.UNKNOWN
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    planner_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    compiler_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    backend_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        # Enforce strict immutability types for collections
        if not isinstance(self.supported_backends, tuple):
            object.__setattr__(self, 'supported_backends', tuple(self.supported_backends))

        if not isinstance(self.required_kernels, tuple):
            object.__setattr__(self, 'required_kernels', tuple(self.required_kernels))

        if not isinstance(self.hardware_requirements, tuple):
            object.__setattr__(self, 'hardware_requirements', tuple(self.hardware_requirements))

        if not isinstance(self.recommended_hardware, tuple):
            object.__setattr__(self, 'recommended_hardware', tuple(self.recommended_hardware))

        if not isinstance(self.conversion_compatibility, tuple):
            object.__setattr__(self, 'conversion_compatibility', tuple(self.conversion_compatibility))

        if not isinstance(self.compression_metadata, MappingProxyType):
            object.__setattr__(self, 'compression_metadata', MappingProxyType(self.compression_metadata))

        if not isinstance(self.supported_model_families, tuple):
            object.__setattr__(self, 'supported_model_families', tuple(self.supported_model_families))

        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, 'metadata', MappingProxyType(self.metadata))

        if not isinstance(self.planner_metadata, MappingProxyType):
            object.__setattr__(self, 'planner_metadata', MappingProxyType(self.planner_metadata))

        if not isinstance(self.compiler_metadata, MappingProxyType):
            object.__setattr__(self, 'compiler_metadata', MappingProxyType(self.compiler_metadata))

        if not isinstance(self.backend_metadata, MappingProxyType):
            object.__setattr__(self, 'backend_metadata', MappingProxyType(self.backend_metadata))
