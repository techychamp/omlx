# SPDX-License-Identifier: Apache-2.0
"""
Immutable Quantization Descriptor.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple, Optional
from .types import QuantizationFamily, ValidationStatus

@dataclass(frozen=True)
class QuantizationDescriptor:
    """
    Immutable canonical representation of a quantization config.
    """
    quantization_family: QuantizationFamily
    storage_precision: str
    compute_precision: str
    weight_precision: str
    activation_precision: str
    kv_cache_precision: str
    group_size: Optional[int]
    block_size: Optional[int]
    mixed_precision: bool
    dynamic_quantization: bool
    static_quantization: bool
    per_channel: bool
    per_group: bool
    supports_streaming: bool
    supports_batching: bool
    supports_speculative_decoding: bool
    supported_backends: Tuple[str, ...]
    supported_model_families: Tuple[str, ...]
    packing_information: Optional[str]
    compression_metadata: MappingProxyType[str, Any]
    required_kernels: Tuple[str, ...]
    hardware_requirements: Tuple[str, ...]
    validation_status: ValidationStatus
    metadata: MappingProxyType[str, Any]
    planner_metadata: MappingProxyType[str, Any]
    compiler_metadata: MappingProxyType[str, Any]
    backend_metadata: MappingProxyType[str, Any]

    def __post_init__(self):
        # Enforce strict immutability types for collections
        if not isinstance(self.supported_backends, tuple):
            object.__setattr__(self, 'supported_backends', tuple(self.supported_backends))

        if not isinstance(self.required_kernels, tuple):
            object.__setattr__(self, 'required_kernels', tuple(self.required_kernels))

        if not isinstance(self.hardware_requirements, tuple):
            object.__setattr__(self, 'hardware_requirements', tuple(self.hardware_requirements))

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
