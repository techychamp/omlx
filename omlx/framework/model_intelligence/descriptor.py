# SPDX-License-Identifier: Apache-2.0
"""
Unified Model Descriptor.

Provides an immutable representation of a discovered model.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Any, List, Optional, Tuple, Set

@dataclass(frozen=True)
class ModelDescriptor:
    """
    Immutable canonical representation of a model.
    """
    model_id: str
    model_family: str
    architecture: str
    task: str
    modality: str
    parameter_count: int
    hidden_size: int
    layer_count: int
    attention_type: str
    activation_type: str
    kv_cache_support: bool
    speculative_support: bool
    streaming_support: bool
    expert_support: bool
    vision_support: bool
    audio_support: bool
    tool_support: bool
    embedding_support: bool
    reranking_support: bool
    quantization_support: bool
    backend_requirements: Tuple[str, ...]
    planner_metadata: MappingProxyType[str, Any]
    compiler_metadata: MappingProxyType[str, Any]

    def __post_init__(self):
        # Enforce strict immutability types for collections
        if not isinstance(self.backend_requirements, tuple):
            object.__setattr__(self, 'backend_requirements', tuple(self.backend_requirements))

        if not isinstance(self.planner_metadata, MappingProxyType):
            object.__setattr__(self, 'planner_metadata', MappingProxyType(self.planner_metadata))

        if not isinstance(self.compiler_metadata, MappingProxyType):
            object.__setattr__(self, 'compiler_metadata', MappingProxyType(self.compiler_metadata))
