# SPDX-License-Identifier: Apache-2.0
"""
Backend Operations and Graphs.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class BackendOperation:
    """Extremely generic base class for all backend operations."""
    id: str
    inputs: tuple[str, ...] = tuple()
    outputs: tuple[str, ...] = tuple()
    dependencies: tuple[str, ...] = tuple()
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class BackendOperationGraph:
    """Immutable collection of translated backend-native operations."""
    backend_id: str
    operations: MappingProxyType[str, BackendOperation]
    roots: tuple[str, ...]
    barriers: tuple[str, ...] = tuple()
    synchronization_points: tuple[str, ...] = tuple()
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class ReferenceBackendOperation(BackendOperation):
    """Intermediate reference class for reference backends (e.g. MLX, hypothetical CPU/CUDA references)."""
    execution_family: str | None = None

@dataclass(frozen=True)
class MLXOperation(ReferenceBackendOperation):
    """Base class for all MLX-specific compiled operations."""
    pass

@dataclass(frozen=True)
class MLXForwardOperation(MLXOperation):
    """Represents an MLX forward pass operation."""
    pass

@dataclass(frozen=True)
class MLXSamplingOperation(MLXOperation):
    """Represents an MLX token sampling operation."""
    pass

@dataclass(frozen=True)
class MLXCacheLookupOperation(MLXOperation):
    """Represents an MLX KV-cache lookup operation."""
    pass

@dataclass(frozen=True)
class MLXCacheUpdateOperation(MLXOperation):
    """Represents an MLX KV-cache write/update operation."""
    pass

@dataclass(frozen=True)
class MLXSynchronizationOperation(MLXOperation):
    """Represents an MLX/Metal stream synchronization barrier."""
    pass

@dataclass(frozen=True)
class MLXNoOpOperation(MLXOperation):
    """Represents an MLX dummy/no-op placeholder operation."""
    pass
