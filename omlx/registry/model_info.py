# SPDX-License-Identifier: Apache-2.0
"""
Central source-of-truth for loaded models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from omlx.inference.attention import AttentionMode
    from omlx.inference.modes import GenerationMode
    from omlx.runtime.capabilities import ModelCapabilities


__all__ = ["ModelInfo", "build_model_info"]


@dataclass
class ModelInfo:
    """Central source-of-truth for runtime behavior.
    
    Note: does NOT contain scheduler_class. Routing is based on
    preferred_generation_mode via the capability registry.
    """
    model_path: str
    architecture: str
    config_model_type: str
    capabilities: ModelCapabilities
    generation_modes: list[GenerationMode]
    preferred_generation_mode: GenerationMode
    cache_type: str | None   # "kv", "rotating_kv", "arrays", "tq", None
    attention_modes: list[AttentionMode]
    supports_streaming: bool
    tokenizer_info: dict[str, Any]


def build_model_info(
    model_path: str,
    model: Any,
    tokenizer: Any,
    capabilities: ModelCapabilities,
) -> ModelInfo:
    """Construct ModelInfo from a loaded model and tokenizer."""
    from omlx.inference.attention import AttentionMode
    from omlx.inference.modes import GenerationMode
    
    # Infer basic properties
    config = getattr(model, "config", {})
    if not isinstance(config, dict):
        config = getattr(config, "__dict__", {})
        
    architecture = config.get("architectures", ["Unknown"])[0]
    config_model_type = config.get("model_type", "unknown")
    
    # Determine cache type based on known architectures
    cache_type = "kv"
    
    # Determine supported modes
    modes = [GenerationMode.AUTOREGRESSIVE]
    attention_modes = [AttentionMode.CAUSAL]
    preferred_mode = GenerationMode.AUTOREGRESSIVE
    
    if capabilities.supports_diffusion:
        modes.append(GenerationMode.DIFFUSION)
        attention_modes.append(AttentionMode.DIFFUSION)
        preferred_mode = GenerationMode.DIFFUSION
    elif capabilities.supports_linear_speculation:
        modes.append(GenerationMode.LINEAR_SPECULATION)
        attention_modes.append(AttentionMode.VERIFY)
        preferred_mode = GenerationMode.LINEAR_SPECULATION
        
    return ModelInfo(
        model_path=model_path,
        architecture=architecture,
        config_model_type=config_model_type,
        capabilities=capabilities,
        generation_modes=modes,
        preferred_generation_mode=preferred_mode,
        cache_type=cache_type,
        attention_modes=attention_modes,
        supports_streaming=capabilities.supports_streaming,
        tokenizer_info={},
    )
