# SPDX-License-Identifier: Apache-2.0
"""
Feature flags for OMLX inference runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


__all__ = ["FeatureFlags"]


@dataclass
class FeatureFlags:
    """Feature flags gating experimental generation paths.
    
    This is instantiated per-engine via engine config, NOT as a global singleton.
    """
    DIFFUSION_ENABLED: bool = False
    LINEAR_SPEC_ENABLED: bool = False
    SHARED_CACHE_ENABLED: bool = False
    VERIFY_ATTENTION_ENABLED: bool = False

    @classmethod
    def from_env(cls) -> FeatureFlags:
        """Read flags from OMLX_FEATURE_* environment variables."""
        return cls(
            DIFFUSION_ENABLED=os.getenv("OMLX_FEATURE_DIFFUSION", "0") == "1",
            LINEAR_SPEC_ENABLED=os.getenv("OMLX_FEATURE_LINEAR_SPEC", "0") == "1",
            SHARED_CACHE_ENABLED=os.getenv("OMLX_FEATURE_SHARED_CACHE", "0") == "1",
            VERIFY_ATTENTION_ENABLED=os.getenv("OMLX_FEATURE_VERIFY_ATTENTION", "0") == "1",
        )
