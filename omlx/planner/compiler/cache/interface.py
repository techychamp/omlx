# SPDX-License-Identifier: Apache-2.0
"""
Compiler Cache Interface.
"""
import abc
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, Optional

T = TypeVar("T")

@dataclass(frozen=True)
class CacheEntry(Generic[T]):
    """An entry in the compiler cache."""
    key: str
    value: T
    size_bytes: int
    version: str

class CompilerCacheInterface(abc.ABC):
    """Abstract interface for a compiler cache."""

    @abc.abstractmethod
    def get(self, key: str) -> Optional[CacheEntry[Any]]:
        """Retrieve an item from the cache."""
        pass

    @abc.abstractmethod
    def put(self, key: str, value: Any, size_bytes: int, version: str) -> None:
        """Add an item to the cache."""
        pass

    @abc.abstractmethod
    def invalidate(self, key: str) -> None:
        """Invalidate a specific key in the cache."""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear the entire cache."""
        pass

    @abc.abstractmethod
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        pass
