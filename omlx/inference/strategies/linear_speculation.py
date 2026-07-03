# SPDX-License-Identifier: Apache-2.0
"""
Linear speculation generation strategy stub.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from omlx.inference.modes import GenerationMode
from omlx.inference.strategy import BaseGenerationStrategy
from omlx.inference.strategy_types import ForwardResult, PostprocessResult, PrefillResult

if TYPE_CHECKING:
    from omlx.request import RequestOutput
    from omlx.runtime.capabilities import ActualCapabilities
    from omlx.runtime.generation_request import GenerationRequest
    from omlx.runtime.context import GenerationContext, RuntimeState
    from omlx.inference.streaming import StreamingDelta


__all__ = ["LinearSpeculationStrategy"]


class LinearSpeculationStrategy(BaseGenerationStrategy):
    """Stub strategy for linear speculative decoding (Phase 1)."""

    @property
    def mode(self) -> GenerationMode:
        return GenerationMode.LINEAR_SPECULATION

    def is_streaming_capable(self) -> bool:
        return True

    def make_context(
        self, request: Any, capabilities: ActualCapabilities
    ) -> tuple[GenerationContext, RuntimeState]:
        from omlx.inference.attention import AttentionMode
        from omlx.inference.sampler_interface import SamplerParams, make_sampler_interface
        from omlx.runtime.context import GenerationContext, RuntimeState
        
        req_params = request.sampling_params
        sampler_params = SamplerParams(
            temperature=req_params.temperature,
            top_p=req_params.top_p,
            top_k=req_params.top_k,
            min_p=req_params.min_p,
            xtc_probability=req_params.xtc_probability,
            xtc_threshold=req_params.xtc_threshold,
            repetition_penalty=req_params.repetition_penalty,
        )
        
        # Note: Uses causal attention. Verificiation uses VERIFY attention mode.
        ctx = GenerationContext(
            request_id=request.request_id,
            generation_mode=self.mode,
            attention_mode=AttentionMode.CAUSAL,
            sampler=make_sampler_interface(sampler_params),
            capabilities=capabilities,
            prompt_tokens=tuple(request.prompt_token_ids or []),
            max_tokens=request.sampling_params.max_tokens,
        )
        state = RuntimeState()
        return ctx, state

    def prefill(self, requests: list[GenerationRequest]) -> list[PrefillResult]:
        return [PrefillResult(prompt_cache=None, cached_tokens=0) for _ in requests]

    def forward(self, requests: list[GenerationRequest]) -> list[ForwardResult]:
        raise NotImplementedError("Linear speculation forward not implemented yet.")

    def sample(
        self, ctx: GenerationContext, state: RuntimeState, logits: Any
    ) -> Any:
        raise NotImplementedError("LinearSpeculation sample not implemented yet.")

    def postprocess(
        self, requests: list[GenerationRequest], results: list[ForwardResult]
    ) -> list[PostprocessResult]:
        raise NotImplementedError("Linear speculation postprocess not implemented yet.")

    def emit(
        self, requests: list[GenerationRequest], results: list[PostprocessResult]
    ) -> list[StreamingDelta]:
        return []
