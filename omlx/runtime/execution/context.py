# SPDX-License-Identifier: Apache-2.0
"""
Execution Context for OMLX Execution Engine.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass(frozen=True)
class ExecutionContext:
    """Immutable snapshot of the execution context."""
    request_context: Any = None
    execution_plan: Optional[Any] = None
    logical_ir: Optional[Any] = None
    physical_ir: Optional[Any] = None
    backend_operation_graph: Optional[Any] = None
    compiler_session: Optional[Any] = None
    capability_descriptor: Optional[Any] = None
    model_descriptor: Optional[Any] = None
    quantization_descriptor: Optional[Any] = None
    execution_policy: Optional[Any] = None
    backend_selection: Optional[Any] = None
    diagnostics: Optional[Any] = None
    statistics: Optional[Any] = None
