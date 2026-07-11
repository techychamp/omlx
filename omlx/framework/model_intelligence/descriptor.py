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
    model_id: str = ""
    model_family: str = ""
    architecture: str = ""
    architecture_family: str = ""
    architecture_generation: str = ""
    task: str = ""
    modality: str = ""
    parameter_count: int = 0
    hidden_size: int = 0
    layer_count: int = 0
    context_length: int = 0
    attention_type: str = ""
    activation_type: str = ""
    tokenizer_family: str = ""
    special_token_information: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    moe_information: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    expert_count: int = 0
    expert_size: int = 0
    kv_cache_support: bool = False
    speculative_support: bool = False
    streaming_support: bool = False
    expert_support: bool = False
    vision_support: bool = False
    audio_support: bool = False
    tool_support: bool = False
    embedding_support: bool = False
    reranking_support: bool = False
    quantization_support: bool = False
    backend_requirements: Tuple[str, ...] = field(default_factory=tuple)
    license: str = ""
    repository_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    recommended_backend: str = ""
    recommended_quantization: str = ""
    recommended_execution_mode: str = ""
    recommended_scheduler: str = ""
    compatibility_report: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    validation_report: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    planner_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    compiler_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        # Enforce strict immutability types for collections
        if not isinstance(self.backend_requirements, tuple):
            object.__setattr__(self, 'backend_requirements', tuple(self.backend_requirements))

        if not isinstance(self.special_token_information, MappingProxyType):
            object.__setattr__(self, 'special_token_information', MappingProxyType(self.special_token_information))

        if not isinstance(self.moe_information, MappingProxyType):
            object.__setattr__(self, 'moe_information', MappingProxyType(self.moe_information))

        if not isinstance(self.repository_metadata, MappingProxyType):
            object.__setattr__(self, 'repository_metadata', MappingProxyType(self.repository_metadata))

        if not isinstance(self.compatibility_report, MappingProxyType):
            object.__setattr__(self, 'compatibility_report', MappingProxyType(self.compatibility_report))

        if not isinstance(self.validation_report, MappingProxyType):
            object.__setattr__(self, 'validation_report', MappingProxyType(self.validation_report))

        if not isinstance(self.planner_metadata, MappingProxyType):
            object.__setattr__(self, 'planner_metadata', MappingProxyType(self.planner_metadata))

        if not isinstance(self.compiler_metadata, MappingProxyType):
            object.__setattr__(self, 'compiler_metadata', MappingProxyType(self.compiler_metadata))
