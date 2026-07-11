# SPDX-License-Identifier: Apache-2.0
"""
ExecutionGroup for OMLX Scheduling subsystem.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Any

@dataclass(frozen=True)
class ExecutionGroup:
    """Immutable collection of operations that can be executed together."""
    group_id: str
    operations: Tuple[str, ...] = field(default_factory=tuple)
    dependency_level: int = 0
    estimated_cost: float = 0.0
    estimated_memory: float = 0.0
    parallelizable: bool = False
    priority: int = 0
