# SPDX-License-Identifier: Apache-2.0
"""
Capability Resolver Subsystem.
Responsible for merging metadata into an immutable CapabilityDescriptor.
"""

from .descriptor import (
    CapabilityDescriptor,
    ExecutionFamily,
    AttentionType,
    CacheLayoutType
)
from .exceptions import CapabilityValidationError, CapabilityConflictError
from .resolver import CapabilityResolver
from .sources import (
    CapabilitySource,
    ModelMetadataSource,
    FeatureFlagSource,
    RuntimeOverrideSource,
    PluginSource
)

__all__ = [
    "CapabilityDescriptor",
    "ExecutionFamily",
    "AttentionType",
    "CacheLayoutType",
    "CapabilityValidationError",
    "CapabilityConflictError",
    "CapabilityResolver",
    "CapabilitySource",
    "ModelMetadataSource",
    "FeatureFlagSource",
    "RuntimeOverrideSource",
    "PluginSource"
]
