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


__all__ = [
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
]
