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
    """Execution engine for standard Transformer models using standard graph execution."""
    
    def __init__(self, batch_generator: Any = None):
        # batch_generator is kept for API compatibility, but we don't use mlx_lm
        self.batch_generator = batch_generator
        self._graph_execution_enabled = True

    def has_generator(self) -> bool:
        """Check if the generator is initialized."""
        return True # Native compiler handles this now

    def ensure_generator(self, scheduler: Any, sampling_params: Any) -> None:
        """Initialize standard graph execution. No longer uses mlx_lm.generate.BatchGenerator."""
        self._graph_execution_enabled = True

    def insert(self, *args: Any, **kwargs: Any) -> list[int]:
        """Mock insert for compatibility."""
        return [0]

    def remove(self, *args: Any, **kwargs: Any) -> None:
        """Mock remove for compatibility."""
        pass

    def extract_cache(self, *args: Any, **kwargs: Any) -> Any:
        """Mock extract_cache for compatibility."""
        return None

    def eval_cache(self) -> int:
        """Mock eval_cache for compatibility."""
        return 0

    def forward(self, inputs: Any = None) -> Any:
        """Perform a single step forward pass via the compiler runtime."""
        if hasattr(self.batch_generator, "next_generated"):
            return self.batch_generator.next_generated()
        raise NotImplementedError("Compiler-native Runtime owns generation.")
        return []
