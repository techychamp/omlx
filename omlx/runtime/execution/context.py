# SPDX-License-Identifier: Apache-2.0
"""
Execution Context for OMLX Execution Engine.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, TYPE_CHECKING
from omlx.runtime.execution.artifacts import ExecutionGraph

if TYPE_CHECKING:
    from omlx.planner.domains.speculation.artifacts import SpeculativeExecutionGraph

@dataclass(frozen=True)
class AppleExecutionMetadata:
    """Immutable metadata for Apple Silicon execution context."""
    device_plan: Optional[Any] = None
    placement: Optional[Any] = None
    optimization_report: Optional[Any] = None

@dataclass(frozen=True)
class DeviceContext:
    """Immutable device configuration and constraints."""
    device_id: Optional[str] = None
    memory_limit: Optional[int] = None
    compute_capability: Optional[str] = None

@dataclass(frozen=True)
class MemoryContext:
    """Immutable memory allocation plan and bounds."""
    total_allocated: int = 0
    pinned_memory: int = 0
    memory_strategy: Optional[str] = None


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable snapshot of the execution context.
    
    Acts as the central transport object for carrying compilation plans, 
    execution graphs, and platform-specific metadata (e.g., AppleExecutionMetadata) 
    to the runtime execution backend, without tightly coupling the engine to 
    specific platform implementations. Future integrations (e.g. CUDA, ROCm) 
    should follow this pattern by attaching their respective metadata to this context.
    """
    request_context: Any = None
    execution_plan: Optional[Any] = None
    planning_bundle: Optional[Any] = None
    logical_ir: Optional[Any] = None
    physical_ir: Optional[Any] = None
    backend_operation_graph: Optional[Any] = None
    diffusion_execution_graph: Optional[Any] = None
    speculative_execution_graph: Optional['SpeculativeExecutionGraph'] = None
    execution_graphs: Optional[Tuple[ExecutionGraph, ...]] = None
    compiler_session: Optional[Any] = None
    capability_descriptor: Optional[Any] = None
    model_descriptor: Optional[Any] = None
    quantization_descriptor: Optional[Any] = None
    execution_policy: Optional[Any] = None
    backend_selection: Optional[Any] = None
    diagnostics: Optional[Any] = None
    statistics: Optional[Any] = None
    adapter: Optional[Any] = None
    cache_plan: Optional[Any] = None
    cache_session: Optional[Any] = None
    apple_execution_metadata: Optional[AppleExecutionMetadata] = None

    # MOE Execution Context
    expert_execution_graph: Optional[Any] = None
    routing_reports: Optional[Any] = None
    # Loaded model and tokenizer — injected by the execution harness for RUN-001.
    # The backend adapter does not read these in RUN-001; they are reserved for
    # BACKEND-005 where MLXAdapter.execute() will invoke real MLX kernel dispatch.
    model: Optional[Any] = None
    tokenizer: Optional[Any] = None

