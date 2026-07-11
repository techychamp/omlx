# SPDX-License-Identifier: Apache-2.0
"""
Immutable cache descriptors.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple

@dataclass(frozen=True)
class CacheDescriptor:
    """Immutable description of cache capabilities or configuration."""
    cache_type: str
    capacity: int
    element_size: int
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class CacheCompatibilityReport:
    """Immutable compatibility report for cache."""
    is_compatible: bool
    reasons: Tuple[str, ...] = tuple()
    warnings: Tuple[str, ...] = tuple()

@dataclass(frozen=True)
class CacheStatistics:
    """Immutable cache statistics."""
    hits: int
    misses: int
    allocations: int
    evictions: int
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class CacheValidationReport:
    """Immutable validation report for cache plans."""
    is_valid: bool
    errors: Tuple[str, ...] = tuple()
    warnings: Tuple[str, ...] = tuple()
