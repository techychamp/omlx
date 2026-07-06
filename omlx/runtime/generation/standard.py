# SPDX-License-Identifier: Apache-2.0

import time
import logging
import uuid
from typing import Any

from .strategy import GenerationStrategy
from omlx.runtime.streaming.types import StreamingToken, StreamCompletion
from omlx.runtime.streaming.events import StreamingEvent, StreamingEventType
from omlx.runtime.observability import get_observer, set_observer, reset_observer, Observer
from omlx.runtime.events import Event, RuntimeLifecycleEvent, EventCategory

logger = logging.getLogger("omlx.runtime.generation.standard")

class StandardGenerationStrategy(GenerationStrategy):
    """
    Standard generation strategy that preserves existing Runtime behavior.
    """

    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:
        max_tokens = kwargs.get("max_tokens", 10)
        sampler = kwargs.get("sampler", 0.0)

        with runtime._generate_lock:
            try:
                import mlx.core as mx
            except ImportError:
                mx = None

            run_id = str(uuid.uuid4())
            session_observer = Observer(run_id=run_id)
            set_observer(session_observer)

            try:
                model_id, prompt, model, tokenizer = runtime._prepare_generation_context(request_context)
                translation_result = runtime._compile_request(model_id, request_context)
                backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None))
                adapter = runtime._resolve_adapter(translation_result)

                session = runtime.streaming_controller.create_session()
                input_ids = tokenizer.encode(prompt)

                generated_tokens = []
                generated_text = ""
                status = "success"

                with get_observer().observe_phase("Execution", "Runtime", "generate"):
                    try:
                        for step in range(max_tokens):
                            if not session.is_active:
                                break

                            execution_result = runtime._execute_forward_pass(
                                backend_op_graph, input_ids, translation_result, adapter, model, tokenizer
                            )

                            if execution_result.status.value == "failed":
                                raise RuntimeError("Execution failed")

                            next_token, token_text = runtime._sample_token(execution_result, sampler, mx)

                            if token_text is None:
                                token_text = tokenizer.decode([next_token])

                            generated_tokens.append(next_token)
                            generated_text += token_text

                            stream_token = StreamingToken(
                                token_id=next_token,
                                decoded_text=token_text,
                                timestamp=time.time(),
                                sequence_index=step
                            )

                            runtime.streaming_controller.publish_event(session.session_id, StreamingEvent(
                                event_type=StreamingEventType.TOKEN_GENERATED,
                                timestamp=time.time(),
                                payload={"token": stream_token}
                            ))

                            input_ids.append(next_token)

                            if hasattr(tokenizer, "eos_token_id") and next_token == tokenizer.eos_token_id:
                                break

                        runtime.streaming_controller.complete_session(session.session_id, StreamCompletion.SUCCESS)

                    except Exception as e:
                        status = "failed"
                        runtime.streaming_controller.complete_session(session.session_id, StreamCompletion.ERROR, e)
                        get_observer().add_diagnostic(f"Execution Error: {str(e)}")
                        logger.error(f"ExecutionError in generation loop: {e}")

                end_time = time.time()
                observation_session = session_observer.build_session(
                    end_time=end_time,
                    status=status,
                    generated_tokens=generated_tokens,
                    statistics={"total_tokens": len(generated_tokens), "max_tokens": max_tokens}
                )

                if hasattr(runtime, 'event_bus'):
                    runtime.event_bus.publish(Event(
                        type="observation_session_completed",
                        category=EventCategory.RUNTIME,
                        payload={"session": observation_session}
                    ))

                return {
                    "generated_text": generated_text,
                    "tokens": generated_tokens,
                    "session": session,
                    "observation_session": observation_session
                }
            finally:
                reset_observer()
