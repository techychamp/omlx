# SPDX-License-Identifier: Apache-2.0
"""
Model and engine capabilities for OMLX inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .feature_flags import FeatureFlags


__all__ = ["ModelCapabilities", "EngineCapabilities", "ActualCapabilities", "infer_capabilities"]


@dataclass
class ModelCapabilities:
    """Capabilities inherent to the model architecture itself."""
    supports_autoregressive: bool = True
    supports_diffusion: bool = False
    supports_linear_speculation: bool = False
    supports_mtp: bool = False
    supports_streaming: bool = True
    supports_kv_cache: bool = True
    supports_shared_cache: bool = False
    supports_prefix_cache: bool = True
    supports_chunked_prefill: bool = True
    supports_specprefill: bool = False


@dataclass
class EngineCapabilities:
    """Capabilities supported by the engine hosting the model."""
    supports_diffusion: bool = False
    supports_linear_spec: bool = False
    supports_turboquant: bool = False
    supports_shared_cache: bool = False
    supports_flash_attention: bool = False
    supports_streaming: bool = True


@dataclass
class ActualCapabilities:
    """Intersection of ModelCapabilities, EngineCapabilities, and FeatureFlags.
    
    This is the ground truth for what the runtime will actually execute.
    """
    supports_autoregressive: bool = True
    supports_diffusion: bool = False
    supports_linear_speculation: bool = False
    supports_streaming: bool = True
    supports_shared_cache: bool = False

    @staticmethod
    def resolve(
        model: ModelCapabilities,
        engine: EngineCapabilities,
        flags: FeatureFlags,
    ) -> ActualCapabilities:
        """Resolve actual capabilities by intersecting model, engine, and flags."""
        return ActualCapabilities(
            supports_autoregressive=model.supports_autoregressive,
            supports_diffusion=(
                model.supports_diffusion
                and engine.supports_diffusion
                and flags.DIFFUSION_ENABLED
            ),
            supports_linear_speculation=(
                model.supports_linear_speculation
                and engine.supports_linear_spec
                and flags.LINEAR_SPEC_ENABLED
            ),
            supports_streaming=(
                model.supports_streaming and engine.supports_streaming
            ),
            supports_shared_cache=(
                model.supports_shared_cache
                and engine.supports_shared_cache
                and flags.SHARED_CACHE_ENABLED
            ),
        )


def infer_capabilities(
    model: Any = None,
    model_path: str | Any | None = None,
    config: dict | None = None,
) -> ModelCapabilities:
    """Infer ModelCapabilities from config dict and/or loaded model.
    
    Works with config dict alone (for discovery scans) AND with a loaded
    model object (for post-load refinement). Config-only path returns
    conservative (mostly False) capabilities.
    """
    caps = ModelCapabilities()
    
    if config:
        model_type = config.get("model_type", "")
        # Future-proofing: check for known non-AR model types here
        # Example:
        if "diffusion" in model_type or model_type == "nemotron_labs_diffusion":
             caps.supports_diffusion = True
            
        architectures = config.get("architectures", [])
        # Check architecture hints
        
    if model is not None:
        # Refine based on actual model attributes if available
        if hasattr(model, "diffusion_head"):
            caps.supports_diffusion = True
        if hasattr(model, "draft_model"):
            caps.supports_linear_speculation = True
            
    return caps
