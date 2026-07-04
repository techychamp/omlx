# SPDX-License-Identifier: Apache-2.0
"""
Cache Invalidation logic for Compiler Caches.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Set

class InvalidationReason(Enum):
    VERSION_MISMATCH = "version_mismatch"
    FEATURE_FLAG_CHANGED = "feature_flag_changed"
    BACKEND_CHANGED = "backend_changed"
    PLANNER_CHANGED = "planner_changed"
    ADAPTER_CHANGED = "adapter_changed"
    DESCRIPTOR_CHANGED = "descriptor_changed"
    COMPILER_VERSION_CHANGED = "compiler_version_changed"

@dataclass(frozen=True)
class InvalidationContext:
    reason: InvalidationReason
    details: str

class CacheInvalidationPolicy:
    """Policy for determining when to invalidate cache entries."""
    def __init__(self, compiler_version: str):
        self.compiler_version = compiler_version

    def should_invalidate(self, entry_version: str) -> bool:
        """Check if an entry should be invalidated based on version."""
        return entry_version != self.compiler_version
