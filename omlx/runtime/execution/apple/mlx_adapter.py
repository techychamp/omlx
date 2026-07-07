# SPDX-License-Identifier: Apache-2.0
"""
Runtime MLX Execution Adapter.

This module implements the runtime execution side of the MLX backend.
It is responsible for translating canonical runtime operations into Apple Silicon hardware
instructions via MLX, specifically consuming AppleOptimizationReport and DevicePlan metadata
provided by the compiler layer.
"""

import time
import logging
from typing import Any

from omlx.planner.compiler.backend.operations import (
    BackendOperation,
    MLXForwardOperation,
    MLXSynchronizationOperation,
    MLXCacheLookupOperation,
    MLXCacheUpdateOperation,
    MLXSamplingOperation,
    MLXNoOpOperation,
)
from omlx.runtime.observability import get_observer
from omlx.runtime.execution.context import ExecutionContext

logger = logging.getLogger("omlx.runtime.execution.apple.mlx_adapter")


class MLXRuntimeAdapter:
    """
    Runtime execution adapter for MLX on Apple Silicon.
    Consumes compiled backend operations and AppleExecutionMetadata.
    """
    def __init__(self):
        self._pending_evals = []
        self._raw_statistics = {
            "total_execution_latency_ms": 0.0,
            "total_memory_transfers": 0,
            "total_placement_validations": 0,
            "total_operations_batched": 0,
            "total_batches_executed": 0,
            "total_synchronization_events": 0,
            "execution_reports": []
        }
        self._metal_metrics = {
            "peak_memory_bytes": None,
            "active_memory_bytes": None,
            "cache_memory_bytes": None
        }
        self._memory_report = None
        self._placement_report = None

    def execute(self, operation: BackendOperation, context: ExecutionContext) -> Any:
        """
        Execute a single MLX backend operation.
        Consumes placement and execution configurations specified by the compiler's
        AppleExecutionMetadata without modifying optimization policies.
        """
        start_time = time.perf_counter()
        diagnostics = []
        result_data = {}
        status = "failed"
        error = None

        from omlx.runtime.execution.apple.reports import (
            AppleExecutionPerformanceReport,
            UnifiedMemoryPerformanceReport,
            PlacementExecutionReport
        )
        
        # Extract Apple execution metadata if present
        apple_metadata = getattr(context, "apple_execution_metadata", None)
        
        try:
            import mlx.core as mx
            mlx_available = True
        except ImportError as e:
            mlx_available = False
            diagnostics.append(f"mlx.core is not available ({e}). Execution will be mocked.")

        if apple_metadata:
            device_plan = apple_metadata.device_plan
            optimization_report = apple_metadata.optimization_report
            if device_plan:
                diagnostics.append("Applying DevicePlan constraints during execution.")
            if optimization_report:
                diagnostics.append("Consuming AppleOptimizationReport configuration metadata.")
                
                from omlx.optimization.apple.policy import ExecutionAffinityPreference
                placement_strategy = getattr(optimization_report, "placement_strategy", None)
                memory_policy = getattr(optimization_report, "memory_policy", None)
                affinity = getattr(optimization_report, "affinity_preference", None)

                # Metadata consistency validation
                if placement_strategy and getattr(placement_strategy, "memory_policy", None) and affinity:
                    if placement_strategy.memory_policy.preferred_execution_device == "gpu" and affinity == ExecutionAffinityPreference.CPU:
                        error_msg = "Metadata consistency validation failed: GPU placement with CPU-only execution affinity."
                        diagnostics.append(error_msg)
                        return self._fail_execution(operation.id, error_msg, diagnostics)

                # Consume memory policy
                if memory_policy and self._memory_report is None:
                    cache_limit = None
                    diag_list = ["Memory policy consumed successfully"]
                    if memory_policy.preferred_memory_residency == "unified":
                        if mlx_available and hasattr(mx, "metal") and hasattr(mx.metal, "set_cache_limit"):
                            try:
                                cache_limit_bytes = getattr(memory_policy, "cache_limit_bytes", None)
                                if cache_limit_bytes:
                                    mx.metal.set_cache_limit(cache_limit_bytes)
                                    cache_limit = cache_limit_bytes
                                    diag_list.append("set_cache_limit capability successfully utilized.")
                            except Exception as me:
                                diag_list.append(f"Failed to set cache limit: {me}")
                        else:
                            diag_list.append("set_cache_limit capability unavailable on this MLX version. Skipping.")
                    
                    self._memory_report = UnifiedMemoryPerformanceReport(
                        memory_policy_applied=memory_policy.preferred_memory_residency,
                        cache_limit_bytes=cache_limit,
                        bytes_transferred=0,
                        synchronization_events=0,
                        diagnostics=tuple(diag_list)
                    )

                # Consume placement strategy
                if placement_strategy and self._placement_report is None:
                    diagnostics.append(f"Consuming PlacementStrategy: type={placement_strategy.strategy_type}")
                    self._placement_report = PlacementExecutionReport(
                        placement_strategy_applied=placement_strategy.strategy_type,
                        actual_device="apple_silicon",
                        diagnostics=("Placement strategy consumed successfully",)
                    )
                    self._raw_statistics["total_placement_validations"] += 1

        try:
            if isinstance(operation, MLXForwardOperation):
                if getattr(context, "model", None) is None:
                    diagnostics.append("No model in ExecutionContext. Simulating forward.")
                    result_data = {"logits": "simulated_logits"}
                    status = "executed"
                else:
                    if not mlx_available:
                        diagnostics.append("MLX is not available. Simulating forward pass on real model object.")
                        try:
                            # try to simulate passing input to model to see what it does
                            logits = context.model([0])
                            result_data = {"logits_shape": getattr(logits, "shape", None)}
                            self._pending_evals.append("simulated_array")
                            self._raw_statistics["total_operations_batched"] += 1
                        except Exception as inner_e:
                            diagnostics.append(f"Simulated forward failed: {inner_e}")
                        status = "executed"
                    else:
                        diagnostics.append("Executing real MLX forward pass (batching execution).")
                        # Execute a real forward kernel dispatch
                        input_ids = mx.array([[0]])
                        if getattr(context, "request_context", None) and hasattr(context.request_context, "input_ids"):
                            input_ids = mx.array([context.request_context.input_ids])

                        logits = context.model(input_ids)
                        self._pending_evals.append(logits)
                        self._raw_statistics["total_operations_batched"] += 1
                        result_data = {"logits": logits}
                        status = "executed"

            elif isinstance(operation, MLXSynchronizationOperation):
                if mlx_available:
                    if self._pending_evals:
                        mx.eval(*self._pending_evals)
                        diagnostics.append(f"Synchronized MLX stream (mx.eval on {len(self._pending_evals)} operations).")
                        self._raw_statistics["total_batches_executed"] += 1
                        self._pending_evals.clear()
                    else:
                        mx.eval()
                        diagnostics.append("Synchronized MLX stream (mx.eval empty).")
                    
                    if hasattr(mx, "metal"):
                        if hasattr(mx.metal, "get_peak_memory"):
                            self._metal_metrics["peak_memory_bytes"] = mx.metal.get_peak_memory()
                        if hasattr(mx.metal, "get_active_memory"):
                            self._metal_metrics["active_memory_bytes"] = mx.metal.get_active_memory()
                        if hasattr(mx.metal, "get_cache_memory"):
                            self._metal_metrics["cache_memory_bytes"] = mx.metal.get_cache_memory()
                else:
                    diagnostics.append(f"No MLX to synchronize. Batching simulated ({len(self._pending_evals)} operations).")
                    if self._pending_evals:
                        self._raw_statistics["total_batches_executed"] += 1
                    self._pending_evals.clear()
                
                self._raw_statistics["total_synchronization_events"] += 1
                status = "executed"

            elif isinstance(operation, MLXCacheLookupOperation):
                diagnostics.append("Cache lookup handled via implicit MLX graph.")
                status = "executed"

            elif isinstance(operation, MLXCacheUpdateOperation):
                diagnostics.append("Cache update handled via implicit MLX graph.")
                status = "executed"

            elif isinstance(operation, MLXSamplingOperation):
                diagnostics.append("Sampling operation delegated to Runtime (not a backend responsibility).")
                status = "unsupported"
                error = "SamplingOperation is not supported by MLXRuntimeAdapter. Sampling belongs to the runtime."

            elif isinstance(operation, MLXNoOpOperation):
                diagnostics.append("NoOp operation executed.")
                status = "executed"

            else:
                diagnostics.append(f"Unsupported operation type: {type(operation).__name__}")
                status = "unsupported"
                error = f"Operation '{operation.id}' of type {type(operation).__name__} is not supported."

        except Exception as e:
            status = "failed"
            error = str(e)
            diagnostics.append(f"Execution failed with exception: {str(e)}")
            logger.error(f"Execution failed in MLXRuntimeAdapter: {e}", exc_info=True)
            self._pending_evals.clear()

        execution_duration_ms = (time.perf_counter() - start_time) * 1000
        self._raw_statistics["total_execution_latency_ms"] += execution_duration_ms

        # Passively observe Apple execution metrics if metadata exists
        if apple_metadata and get_observer():
            report_data = {
                "operation_id": operation.id,
                "latency_ms": execution_duration_ms,
                "status": status,
                "has_device_plan": apple_metadata.device_plan is not None,
                "has_optimization_report": apple_metadata.optimization_report is not None,
            }
            # Record execution metadata without taking ownership of placement logic
            get_observer().track_artifact("AppleExecutionMetrics", report_data)

        execution_report = AppleExecutionPerformanceReport(
            operation_id=operation.id,
            latency_ms=execution_duration_ms,
            status=status,
            error_message=error,
            diagnostics=tuple(diagnostics)
        )
        self._raw_statistics["execution_reports"].append(execution_report)

        return {
            "status": status,
            "operation_id": operation.id,
            "backend": "mlx",
            "diagnostics": diagnostics,
            "execution_duration_ms": execution_duration_ms,
            "error": error,
            "result": result_data
        }

    def _fail_execution(self, operation_id: str, error_msg: str, diagnostics: list) -> Any:
        from omlx.runtime.execution.apple.reports import AppleExecutionPerformanceReport
        
        execution_report = AppleExecutionPerformanceReport(
            operation_id=operation_id,
            latency_ms=0.0,
            status="failed",
            error_message=error_msg,
            diagnostics=tuple(diagnostics)
        )
        self._raw_statistics["execution_reports"].append(execution_report)
        return {
            "status": "failed",
            "operation_id": operation_id,
            "backend": "mlx",
            "diagnostics": diagnostics,
            "execution_duration_ms": 0.0,
            "error": error_msg,
            "result": {}
        }
        
    def get_statistics(self) -> dict:
        """Expose collected execution statistics for the ExecutionEngine."""
        return {
            "raw_statistics": self._raw_statistics,
            "metal_metrics": self._metal_metrics,
            "memory_report": self._memory_report,
            "placement_report": self._placement_report
        }
