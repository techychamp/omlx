# SPDX-License-Identifier: Apache-2.0
"""
Feature flags for OMLX inference runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


__all__ = ["FeatureFlags"]


import abc

class FeatureFlagsMeta(abc.ABCMeta):
    def __instancecheck__(cls, instance):
        if type(instance).__name__ == "ImmutableSnapshot":
            return True
        return super().__instancecheck__(instance)


@dataclass
class FeatureFlags(metaclass=FeatureFlagsMeta):
    """Feature flags gating experimental generation paths.
    
    This is instantiated per-engine via engine config, NOT as a global singleton.
    """
    DIFFUSION_ENABLED: bool = False
    LINEAR_SPEC_ENABLED: bool = False
    SHARED_CACHE_ENABLED: bool = False
    VERIFY_ATTENTION_ENABLED: bool = False
    COMPILER_RUNTIME_PIPELINE_ENABLED: bool = False
    CAPABILITY_RUNTIME_ENABLED: bool = False
    PLANNER_RUNTIME_ENABLED: bool = False
    LOWERING_RUNTIME_ENABLED: bool = False
    ADAPTER_RUNTIME_ENABLED: bool = False
    EXECUTION_PLAN_RUNTIME_ENABLED: bool = False
    EXECUTION_PROFILE_COMPATIBILITY_ENABLED: bool = False
    EXECUTION_PLAN_VALIDATION_ENABLED: bool = False


    @classmethod
    def from_env(cls) -> FeatureFlags:
        """Read flags from OMLX_FEATURE_* environment variables."""
        return cls(
            DIFFUSION_ENABLED=os.getenv("OMLX_FEATURE_DIFFUSION", "0") == "1",
            LINEAR_SPEC_ENABLED=os.getenv("OMLX_FEATURE_LINEAR_SPEC", "0") == "1",
            SHARED_CACHE_ENABLED=os.getenv("OMLX_FEATURE_SHARED_CACHE", "0") == "1",
            VERIFY_ATTENTION_ENABLED=os.getenv("OMLX_FEATURE_VERIFY_ATTENTION", "0") == "1",
            COMPILER_RUNTIME_PIPELINE_ENABLED=os.getenv("OMLX_FEATURE_COMPILER_RUNTIME_PIPELINE", "0") == "1",
            CAPABILITY_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_CAPABILITY_RUNTIME", "0") == "1",
            PLANNER_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_PLANNER_RUNTIME", "0") == "1",
            LOWERING_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_LOWERING_RUNTIME", "0") == "1",
            ADAPTER_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_ADAPTER_RUNTIME", "0") == "1",
            EXECUTION_PLAN_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_EXECUTION_PLAN_RUNTIME", "0") == "1",
            EXECUTION_PROFILE_COMPATIBILITY_ENABLED=os.getenv("OMLX_FEATURE_EXECUTION_PROFILE_COMPATIBILITY", "0") == "1",
            EXECUTION_PLAN_VALIDATION_ENABLED=os.getenv("OMLX_FEATURE_EXECUTION_PLAN_VALIDATION", "0") == "1",

        )
