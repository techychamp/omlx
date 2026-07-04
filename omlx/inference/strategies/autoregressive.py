# SPDX-License-Identifier: Apache-2.0
"""
Standard autoregressive (token-by-token) generation strategy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from omlx.inference.modes import GenerationMode
from omlx.inference.strategy import BaseGenerationStrategy
from omlx.inference.strategy_types import ForwardResult, PostprocessResult, PrefillResult
from omlx.request import RequestOutput
from omlx.runtime.context import GenerationContext, RuntimeState

if TYPE_CHECKING:
    from omlx.runtime.capabilities import ActualCapabilities
    from omlx.runtime.generation_request import GenerationRequest


__all__ = ["AutoregressiveStrategy"]


class AutoregressiveStrategy(BaseGenerationStrategy):
    """Standard token-by-token generation strategy."""

    @property
    def mode(self) -> GenerationMode:
        return GenerationMode.AUTOREGRESSIVE

    def is_streaming_capable(self) -> bool:
        return True

    def make_context(
        self, request: Any, capabilities: ActualCapabilities
    ) -> tuple[GenerationContext, RuntimeState]:
        from omlx.inference.attention import AttentionMode
        from omlx.inference.sampler_interface import SamplerParams, make_sampler_interface
        
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
            attention_mode=AttentionMode.CAUSAL,
            sampler=make_sampler_interface(sampler_params),
            capabilities=capabilities,
            prompt_tokens=tuple(request.prompt_token_ids or []),
            max_tokens=request.sampling_params.max_tokens,
        )
        state = RuntimeState()
        return ctx, state

    def __init__(self, scheduler: Any = None, backend: Any = None) -> None:
        super().__init__(scheduler, backend)

    @property
    def decode_executor(self) -> Any:
        """Authoritative execution object for decode iteration."""
        if self.scheduler is not None:
            return self.scheduler.batch_generator
        return None

    @property
    def batch_generator(self) -> Any:
        """For backwards compatibility and mocking in tests."""
        return self.decode_executor

    def forward(self) -> Any:
        """Execute a single execution cycle and return the native decode iterator."""
        bg = self.decode_executor
        if bg is None:
            return iter([])
        return bg.next_generated()

    def sample(
        self, ctx: GenerationContext, state: RuntimeState, logits: Any
    ) -> Any:
        """Phase 1.6b Pass 2: Delegate sampling to the context sampler."""
        return ctx.sampler(logits)

    def emit(
        self, requests: list[GenerationRequest], results: list[PostprocessResult]
    ) -> list[StreamingDelta]:
        """Phase 1.6b Pass 5: Map PostprocessResult to StreamingDelta."""
        from omlx.inference.streaming import StreamingDelta
        
        deltas = []
        for req, res in zip(requests, results):
            metrics = getattr(req.state, "metrics", None)
            delta = StreamingDelta(
                token_ids=res.token_ids,
                text=res.text,
                is_final=res.is_final,
                delta_kind="token",
                metrics_snapshot=metrics,
                finish_reason=res.finish_reason,
            )
            # Carry over the raw response and final result for the Scheduler
            if "raw_response" in res.extra:
                delta.extra["raw_response"] = res.extra["raw_response"]
            if "parser_result" in res.extra:
                delta.extra["parser_result"] = res.extra["parser_result"]
            if "final_result" in res.extra:
                delta.extra["final_result"] = res.extra["final_result"]
            deltas.append(delta)
        return deltas

    def postprocess(
        self, requests: list[GenerationRequest], results: list[ForwardResult]
    ) -> list[PostprocessResult]:
        """Phase 1.6b Pass 4: Decode tokens and evaluate stop conditions."""
        batch_responses = []
        if results and "batch_responses" in results[0].extra:
            batch_responses = results[0].extra["batch_responses"]

        uid_to_resp = {r.uid: r for r in batch_responses}
        post_results = []

        for req in requests:
            rid = req.request_id
            uid = next(
                (u for u, r in self.scheduler.uid_to_request_id.items() if r == rid),
                None,
            )
            response = uid_to_resp.get(uid) if uid is not None else None

            if response is None:
                post_results.append(PostprocessResult())
                continue

            is_stop = response.finish_reason == "stop"
            is_length = response.finish_reason == "length"
            is_finished = response.finish_reason is not None

            new_text = ""
            parser_session = self.scheduler._get_output_parser_session(rid)
            parser_result = None

            if parser_session is not None and not is_stop:
                parser_result = parser_session.process_token(response.token)
                new_text = parser_result.stream_text
                if parser_result.is_stop and not is_finished:
                    is_finished = True
                    is_stop = True
                    response.finish_reason = "stop"

            elif not is_stop:
                detokenizer = self.scheduler._get_detokenizer(rid)
                if detokenizer is not None:
                    detokenizer.add_token(response.token)
                    new_text = detokenizer.last_segment
                else:
                    new_text = self.scheduler.tokenizer.decode([response.token])

                stop_strs = req.sampling_params.stop or []
                if stop_strs and not is_finished and detokenizer is not None:
                    full_text = detokenizer.text
                    prev_len = len(full_text) - len(new_text)
                    for ss in stop_strs:
                        if not ss:
                            continue
                        scan_start = max(0, prev_len - len(ss) + 1)
                        idx_in_tail = full_text.find(ss, scan_start)
                        if idx_in_tail >= 0:
                            is_finished = True
                            is_stop = True
                            response.finish_reason = "stop"
                            if idx_in_tail >= prev_len:
                                new_text = new_text[: idx_in_tail - prev_len]
                            else:
                                new_text = ""
                            break

            final_result = None
            if is_finished:
                if parser_session is not None:
                    final_result = parser_session.finalize()
                else:
                    detokenizer = self.scheduler._get_detokenizer(rid)
                    if detokenizer is not None:
                        detokenizer.finalize()
                        final_segment = detokenizer.last_segment
                        if final_segment:
                            new_text += final_segment

            result = PostprocessResult(
                token_ids=[response.token] if not is_stop else [],
                text=new_text,
                is_final=is_finished,
                finish_reason=response.finish_reason,
            )
            # Pass the raw response back so the Scheduler can extract cache
            result.extra["raw_response"] = response
            if parser_session is not None:
                result.extra["parser_result"] = parser_result
                if is_finished:
                    result.extra["final_result"] = final_result

            post_results.append(result)

        return post_results



    def execute(self, command: Any) -> Any:
        from omlx.inference.execution_backend import ExecuteCycleCommand
        if isinstance(command, ExecuteCycleCommand):
            if self.backend:
                return self.backend.execute(None) # backend pipeline handles the forward pass
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
