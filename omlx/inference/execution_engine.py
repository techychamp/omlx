# SPDX-License-Identifier: Apache-2.0
"""
Execution engine interfaces and implementations for OMLX inference.
"""

from __future__ import annotations

import time
import logging
from typing import Any, Protocol, runtime_checkable, Callable

try:
    import mlx.core as mx
except ImportError:
    mx = None

try:
    from mlx_lm.generate import BatchGenerator
except ImportError:
    BatchGenerator = None

try:
    from mlx_lm.sample_utils import make_logits_processors
except ImportError:
    make_logits_processors = None


from omlx.utils.sampling import make_sampler as omlx_make_sampler

logger = logging.getLogger(__name__)


def _apply_suppress_token_ids(logits: Any, suppress_token_ids: tuple[int, ...]) -> Any:
    if suppress_token_ids:
        logits[..., list(suppress_token_ids)] = mx.array(float("-inf"))
    return logits


def _make_suppress_logits_processor(
    suppress_token_ids: set[int],
) -> Callable[[Any, Any], Any] | None:
    suppress_tuple = tuple(sorted(int(t) for t in suppress_token_ids))
    if not suppress_tuple:
        return None

    def _suppress_logits(tokens: Any, logits: Any) -> Any:
        return _apply_suppress_token_ids(logits, suppress_tuple)

    return _suppress_logits


def _collect_mx_arrays(value: Any, out: list[mx.array]) -> None:
    if isinstance(value, mx.array):
        out.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            _collect_mx_arrays(item, out)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _collect_mx_arrays(item, out)


def _eval_generation_batch_cache(batch_generator: Any) -> int:
    generation_batch = getattr(batch_generator, "_generation_batch", None)
    prompt_cache = getattr(generation_batch, "prompt_cache", None)
    if not prompt_cache:
        return 0
    arrays: list[mx.array] = []
    for cache in prompt_cache:
        state = getattr(cache, "state", None)
        if state is not None:
            _collect_mx_arrays(state, arrays)
    if arrays:
        mx.eval(*arrays)
    return len(arrays)


@runtime_checkable
class ExecutionEngine(Protocol):
    """The lowest-level execution engine (e.g., wrappers around MLX, Torch)."""
    
    def forward(self, inputs: Any) -> Any:
        """Run compute/forward pass."""
        ...


@runtime_checkable
class ExecutionRuntime(Protocol):
    """Abstracts the underlying compute platform (MLX, Torch, Metal) for a backend."""
    
    @property
    def engine(self) -> ExecutionEngine:
        """Get the underlying execution engine."""
        ...


class TransformerExecutionEngine(ExecutionEngine):
    """Execution engine for standard Transformer models, owning the BatchGenerator."""
    
    def __init__(self, batch_generator: Any = None):
        self.batch_generator = batch_generator

    def has_generator(self) -> bool:
        """Check if the generator is initialized."""
        return self.batch_generator is not None

    def ensure_generator(self, scheduler: Any, sampling_params: Any) -> None:
        """Ensure the BatchGenerator exists and is initialized with compatible settings."""
        if self.batch_generator is not None:
            return

        # Build stop tokens
        stop_tokens_set = set(scheduler._get_stop_tokens())
        if sampling_params.stop_token_ids:
            stop_tokens_set.update(sampling_params.stop_token_ids)
        stop_tokens_seq = [[t] for t in stop_tokens_set] if stop_tokens_set else None

        # Build sampler
        sampler = omlx_make_sampler(
            temp=sampling_params.temperature,
            top_p=sampling_params.top_p,
            min_p=sampling_params.min_p,
            top_k=sampling_params.top_k,
            xtc_probability=sampling_params.xtc_probability,
            xtc_threshold=sampling_params.xtc_threshold,
            xtc_special_tokens=scheduler._xtc_special_tokens,
        )

        # Build logits processors
        logits_processors = make_logits_processors(
            repetition_penalty=(
                sampling_params.repetition_penalty
                if sampling_params.repetition_penalty != 1.0
                else None
            ),
            presence_penalty=(
                sampling_params.presence_penalty
                if sampling_params.presence_penalty != 0.0
                else None
            ),
            frequency_penalty=(
                sampling_params.frequency_penalty
                if sampling_params.frequency_penalty != 0.0
                else None
            ),
        )

        suppress_processor = _make_suppress_logits_processor(
            scheduler._model_suppress_tokens
        )
        if suppress_processor is not None:
            logits_processors.append(suppress_processor)

        self.batch_generator = BatchGenerator(
            model=scheduler.model,
            max_tokens=sampling_params.max_tokens,
            stop_tokens=stop_tokens_seq,
            sampler=sampler,
            logits_processors=logits_processors if logits_processors else [],
            prefill_batch_size=1,
            completion_batch_size=scheduler.config.completion_batch_size,
            prefill_step_size=scheduler.config.prefill_step_size,
            stream=scheduler._stream,
        )

    def insert(self, *args: Any, **kwargs: Any) -> list[int]:
        """Insert a request into the batch generator."""
        if self.batch_generator is None:
            raise RuntimeError("BatchGenerator is not initialized. Call ensure_generator first.")
        return self.batch_generator.insert(*args, **kwargs)

    def remove(self, *args: Any, **kwargs: Any) -> None:
        """Remove a request from the batch generator."""
        if self.batch_generator is not None:
            self.batch_generator.remove(*args, **kwargs)

    def extract_cache(self, *args: Any, **kwargs: Any) -> Any:
        """Extract prompt cache from the batch generator."""
        if self.batch_generator is None:
            return None
        return self.batch_generator.extract_cache(*args, **kwargs)

    def eval_cache(self) -> int:
        """Evaluate generation batch cache arrays."""
        if self.batch_generator is None:
            return 0
        return _eval_generation_batch_cache(self.batch_generator)

    def forward(self, inputs: Any = None) -> Any:
        """Perform a single step forward pass of the batch generator."""
        if self.batch_generator is None:
            return []
        if hasattr(self.batch_generator, "next_generated"):
            return self.batch_generator.next_generated()
        return []
