# SPDX-License-Identifier: Apache-2.0
"""
Base strategy interface for generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import mlx.core as mx
    
    from omlx.request import RequestOutput
    from omlx.runtime.capabilities import ActualCapabilities
    from omlx.runtime.generation_request import GenerationRequest
    from omlx.runtime.context import GenerationContext, RuntimeState
    
    from .modes import GenerationMode
    from .strategy_types import ForwardResult, PostprocessResult, PrefillResult
    from .streaming import StreamingDelta


__all__ = ["BaseGenerationStrategy"]


class BaseGenerationStrategy(ABC):
    """Abstract base class for all generation strategies."""
    
    def __init__(self, scheduler: Any = None, backend: Any = None) -> None:
        self.scheduler = scheduler
        self._backend = backend

    @property
    def backend(self) -> Any:
        """The execution backend bound to this strategy."""
        return self._backend

    @property
    @abstractmethod
    def mode(self) -> GenerationMode:
        """The generation mode this strategy implements."""
        ...

    @abstractmethod
    def is_streaming_capable(self) -> bool:
        """Whether this strategy can stream outputs incrementally."""
        ...

    @abstractmethod
    def make_context(
        self, request: Any, capabilities: ActualCapabilities
    ) -> tuple[GenerationContext, RuntimeState]:
        """Create the context and state for a new request."""
        ...

    # --- Execution ---
    
    def prefill(
        self,
        model: Any,
        inputs: Any,
        cache: Any,
        **kwargs: Any,
    ) -> None:
        """Default prefill implementation for standard autoregressive/transformer models."""
        import mlx.core as mx
        model(inputs, cache=cache, **kwargs)
        mx.eval([c.state for c in cache])

    @abstractmethod
    def forward(self) -> Any:
        """Execute a single execution cycle, returning the native decode iterator."""
        ...

    @abstractmethod
    def execute(self, command: Any) -> None:
        """Execute a pipeline command."""
        ...

    # --- Event Handling ---
    
    def handle(self, event: Any) -> None:
        """Handle lifecycle and execution events."""
        pass
