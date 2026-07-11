# SPDX-License-Identifier: Apache-2.0
"""
KV cache policies for generation strategies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .modes import GenerationMode


__all__ = ["CachePolicy", "DefaultCachePolicy"]


class CachePolicy(ABC):
    """Policy for how a generation strategy interacts with the KV cache."""

    @abstractmethod
    def allocate(self, context: Any, num_tokens: int) -> Any:
        """Allocate space for new tokens in the cache."""
        ...

    @abstractmethod
    def merge(self, source: Any, target: Any) -> Any:
        """Merge a source cache into a target cache."""
        ...

    @abstractmethod
    def transition(
        self, cache: Any, from_mode: GenerationMode, to_mode: GenerationMode
    ) -> Any:
        """Transition cache state between generation modes."""
        ...

    @abstractmethod
    def evict(self, cache: Any, num_tokens: int) -> Any:
        """Evict tokens from the cache."""
        ...

    @property
    @abstractmethod
    def supports_shared_prefix(self) -> bool:
        """Whether the policy supports shared prefix caching."""
        ...

    @property
    @abstractmethod
    def supports_partial_accept(self) -> bool:
        """Whether the policy supports partially accepting cached blocks."""
        ...


class DefaultCachePolicy(CachePolicy):
    """Default AR cache policy. All operations pass through to existing cache."""

    def allocate(self, context: Any, num_tokens: int) -> Any:
        # Pass-through: actual allocation happens in the cache implementation
        return context.cache

    def merge(self, source: Any, target: Any) -> Any:
        # Pass-through
        return target

    def transition(
        self, cache: Any, from_mode: GenerationMode, to_mode: GenerationMode
    ) -> Any:
        # Pass-through
        return cache

    def evict(self, cache: Any, num_tokens: int) -> Any:
        # Pass-through
        return cache

    @property
    def supports_shared_prefix(self) -> bool:
        return True

    @property
    def supports_partial_accept(self) -> bool:
        return False
