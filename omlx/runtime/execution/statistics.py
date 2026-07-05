# SPDX-License-Identifier: Apache-2.0
"""
Statistics for OMLX Execution Engine.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(frozen=True)
class ExecutionStatistics:
    """Immutable snapshot of execution statistics."""
    executed_operations: int = 0
    backend_invocations: int = 0
    execution_duration_ms: float = 0.0
    graph_depth: int = 0
    execution_groups: int = 0
    dispatcher_calls: int = 0
    adapter_calls: int = 0
    compiler_execution_count: int = 0
    legacy_fallback_count: int = 0
