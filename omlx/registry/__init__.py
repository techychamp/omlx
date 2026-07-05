# SPDX-License-Identifier: Apache-2.0
"""
Registry components for OMLX tri-mode generation.
"""

from __future__ import annotations

from .capability_registry import (
    CacheHints,
    CapabilityBundle,
    GenerationStrategyRegistry,
    RuntimeRequirements,
    SchedulerHooks,
    UIMetadata,
    register_default_strategies,
)
from .model_info import ModelInfo, build_model_info
from .plugin_discovery import discover_plugins

from .base import (
    RegistryPhase,
    RegistryEntry,
    GenericRegistry,
    RegistryLockedError,
    RegistryDuplicateError,
    RegistryDependencyError,
)

from .core import (
    MetadataCapabilityEntry,
    MetadataCapabilityRegistry,
    MetadataExecutionModeEntry,
    MetadataExecutionModeRegistry,
    MetadataExecutionProfileEntry,
    MetadataExecutionProfileRegistry,
    MetadataAdapterEntry,
    MetadataAdapterRegistry,
    MetadataPluginEntry,
    MetadataPluginRegistry,
    MetadataVerificationEntry,
    MetadataVerificationRegistry,
    MetadataBackendEntry,
    MetadataBackendRegistry,
    RegistryContainer,
)

__all__ = [
    # Legacy exports
    "CacheHints",
    "CapabilityBundle",
    "GenerationStrategyRegistry",
    "ModelInfo",
    "RuntimeRequirements",
    "SchedulerHooks",
    "UIMetadata",
    "build_model_info",
    "discover_plugins",
    "register_default_strategies",

    # Base registry exports
    "RegistryPhase",
    "RegistryEntry",
    "GenericRegistry",
    "RegistryLockedError",
    "RegistryDuplicateError",
    "RegistryDependencyError",

    # Core registry exports
    "MetadataCapabilityEntry",
    "MetadataCapabilityRegistry",
    "MetadataExecutionModeEntry",
    "MetadataExecutionModeRegistry",
    "MetadataExecutionProfileEntry",
    "MetadataExecutionProfileRegistry",
    "MetadataAdapterEntry",
    "MetadataAdapterRegistry",
    "MetadataPluginEntry",
    "MetadataPluginRegistry",
    "MetadataVerificationEntry",
    "MetadataVerificationRegistry",
    "MetadataBackendEntry",
    "MetadataBackendRegistry",
    "RegistryContainer",
]

