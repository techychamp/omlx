# SPDX-License-Identifier: Apache-2.0
"""
Execution context and runtime state for generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .metrics import GenerationMetrics

if TYPE_CHECKING:
    from omlx.inference.attention import AttentionMode
    from omlx.inference.modes import GenerationMode
    from omlx.inference.sampler_interface import SamplerInterface
    from .capabilities import ActualCapabilities


__all__ = ["GenerationContext", "RuntimeState"]


@dataclass(frozen=True)
class GenerationContext:
    """Immutable configuration for a single request's generation.
    
    Created once at request admission. Lives for the request lifetime.
    """
    request_id: str
    generation_mode: GenerationMode
    attention_mode: AttentionMode
    sampler: SamplerInterface
    capabilities: ActualCapabilities
    prompt_tokens: tuple[int, ...]
    max_tokens: int
    metadata: dict[str, Any] = field(default_factory=dict)
    # NOTE: metadata is the one mutable-default-in-frozen exception.
    # Callers should not mutate it after construction.


@dataclass
class RuntimeState:
    """Mutable execution state for a single request."""
    step_index: int = 0
    accepted_tokens: list[int] = field(default_factory=list)
    draft_tokens: list[int] = field(default_factory=list)
    block_state: Any = None
    confidence_scores: Any = None
    denoising_iter: int = 0
    buffers: dict[str, Any] = field(default_factory=dict)
    metrics: GenerationMetrics = field(default_factory=GenerationMetrics)

    def advance(self) -> None:
        """Increment the step counter."""
        self.step_index += 1
