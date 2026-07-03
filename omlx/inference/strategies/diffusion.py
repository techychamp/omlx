# SPDX-License-Identifier: Apache-2.0
"""
Diffusion decoding generation strategy stub.
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


__all__ = ["DiffusionStrategy"]


class DiffusionStrategy(BaseGenerationStrategy):
    """Stub strategy for diffusion decoding (Phase 1)."""

    @property
    def mode(self) -> GenerationMode:
        return GenerationMode.DIFFUSION

    def is_streaming_capable(self) -> bool:
        # Blocks are emitted at once
        return False

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
        
        ctx = GenerationContext(
            request_id=request.request_id,
            generation_mode=self.mode,
            attention_mode=AttentionMode.DIFFUSION,
            sampler=make_sampler_interface(sampler_params),
            capabilities=capabilities,
            prompt_tokens=tuple(request.prompt_token_ids or []),
            max_tokens=request.sampling_params.max_tokens,
        )
        state = RuntimeState()
        return ctx, state

    def __init__(self, scheduler: Any = None, backend: Any = None) -> None:
        super().__init__(scheduler, backend)

    def prefill(self, requests: list[GenerationRequest]) -> list[PrefillResult]:
        return [PrefillResult(prompt_cache=None, cached_tokens=0) for _ in requests]

    def execute(self, command: Any) -> Any:
        from omlx.inference.execution_backend import ExecuteCycleCommand
        if isinstance(command, ExecuteCycleCommand):
            if self.backend:
                return self.backend.execute(command)
        return []

    def handle(self, event: Any) -> None:
        from omlx.runtime.events import ExecutionEvent
        if event.type == ExecutionEvent.AFTER_EMIT:
            ctx = event.data.get("ctx")
            state = event.data.get("state")
            if state is not None:
                state.metrics.record_decode_step()
                
        if self.backend is not None:
            self.backend.prepare(events=[event])

    def forward(self, requests: list[GenerationRequest]) -> list[ForwardResult]:
        # Implementation delegated to the backend pipeline
        return []

    def sample(
        self, ctx: GenerationContext, state: RuntimeState, logits: Any
    ) -> Any:
        return ctx.sampler(logits)

    def postprocess(
        self, requests: list[GenerationRequest], results: list[ForwardResult]
    ) -> list[PostprocessResult]:
        post_results = []
        for req in requests:
            post_results.append(PostprocessResult(
                token_ids=[],
                text="",
                is_final=False,
                finish_reason=None
            ))
        return post_results

    def emit(
        self, requests: list[GenerationRequest], results: list[PostprocessResult]
    ) -> list[StreamingDelta]:
        from omlx.inference.streaming import StreamingDelta
        deltas = []
        for req, res in zip(requests, results):
            metrics = getattr(req.state, "metrics", None)
            delta = StreamingDelta(
                token_ids=res.token_ids,
                text=res.text,
                is_final=res.is_final,
                delta_kind="block",
                metrics_snapshot=metrics,
                finish_reason=res.finish_reason,
            )
            deltas.append(delta)
        return deltas
