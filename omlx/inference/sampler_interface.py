# SPDX-License-Identifier: Apache-2.0
"""
Sampler interface for generation strategies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    import mlx.core as mx

# Use lazy import for make_sampler to avoid circular deps with utils
def _get_make_sampler():
    from omlx.utils.sampling import make_sampler
    return make_sampler


__all__ = ["SamplerParams", "SamplerInterface", "make_sampler_interface"]


@dataclass
class SamplerParams:
    """Parameters for sampling."""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 0
    min_p: float = 0.0
    xtc_probability: float = 0.0
    xtc_threshold: float = 0.0
    repetition_penalty: float = 1.0


@runtime_checkable
class SamplerInterface(Protocol):
    """Protocol for samplers used by generation strategies."""
    def sample(self, logits: mx.array) -> mx.array: ...
    
    @property
    def params(self) -> SamplerParams: ...


class _SamplerWrapper:
    """Wrapper to adapt utils.sampling.make_sampler into SamplerInterface."""
    
    def __init__(self, params: SamplerParams):
        self._params = params
        
        # Create a mock sampling params object that utils.sampling expects
        class MockParams:
            pass
            
        p = MockParams()
        p.temperature = params.temperature
        p.top_p = params.top_p
        p.top_k = params.top_k
        p.min_p = params.min_p
        p.xtc_probability = params.xtc_probability
        p.xtc_threshold = params.xtc_threshold
        p.repetition_penalty = params.repetition_penalty
        
        make_sampler = _get_make_sampler()
        self._sampler_fn = make_sampler(p)
        
    def sample(self, logits: mx.array) -> mx.array:
        return self._sampler_fn(logits)
        
    @property
    def params(self) -> SamplerParams:
        return self._params


def make_sampler_interface(params: SamplerParams) -> SamplerInterface:
    """Wrap omlx.utils.sampling.make_sampler into the typed SamplerInterface."""
    return _SamplerWrapper(params)
