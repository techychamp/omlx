# SPDX-License-Identifier: Apache-2.0
"""
Autoregressive execution backend.
"""

from __future__ import annotations

from typing import Any

from omlx.inference.execution_backend import (
    ExecutionBackend,
    ExecutionEngine,
    ExecutionPipeline,
    ExecutionRuntime,
    ExecutionStage,
    ExecutionContract,
    BackendStatus,
    ExecutionPlan,
    ExtractCacheStage,
    PipelineState,
    ExecuteCycleCommand
)


class AutoregressiveExecutionEngine(ExecutionEngine):
    """Wraps the mlx-lm BatchGenerator."""
    def __init__(self, batch_generator: Any):
        self.batch_generator = batch_generator


class AutoregressiveRuntime(ExecutionRuntime):
    """Abstracts MLX runtime state for AR execution."""
    def __init__(self, engine: AutoregressiveExecutionEngine):
        self._engine = engine

    @property
    def engine(self) -> ExecutionEngine:
        return self._engine


class PrefillStage(ExecutionStage):
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        """Execute prefill (currently handled externally in Scheduler, this is a stub for future)."""
        return inputs


class ForwardStage(ExecutionStage):
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        """Execute a forward pass."""
        engine = runtime.engine
        if not isinstance(engine, AutoregressiveExecutionEngine):
            raise TypeError("Expected AutoregressiveExecutionEngine")
        
        batch_generator = engine.batch_generator
        if batch_generator is None:
            return []
            
        if hasattr(batch_generator, "next_generated"):
            return next(batch_generator.next_generated())
        return inputs


class SampleStage(ExecutionStage):
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        """Sample from logits (currently mlx-lm BatchGenerator handles sampling internally)."""
        return inputs


class EmitStage(ExecutionStage):
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        """Format outputs."""
        return inputs


class AutoregressivePipeline(ExecutionPipeline):
    def describe(self) -> str:
        stages_desc = " -> ".join(stage.__class__.__name__ for stage in self.stages)
        return f"AutoregressivePipeline({stages_desc})"

    def run(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        return self.execute(inputs, runtime)


class AutoregressiveBackend(ExecutionBackend):
    """
    Execution backend for standard autoregressive models.
    Delegates to MLX-LM's BatchGenerator.
    """
    def __init__(self, engine: AutoregressiveExecutionEngine) -> None:
        self._runtime = AutoregressiveRuntime(engine)
        self._pipeline = AutoregressivePipeline(
            stages=[
                PrefillStage(),
                ForwardStage(),
                SampleStage(),
                ExtractCacheStage(),
                EmitStage()
            ]
        )

    @property
    def runtime(self) -> ExecutionRuntime:
        return self._runtime

    @property
    def pipeline(self) -> ExecutionPipeline:
        return self._pipeline

    @property
    def contract(self) -> ExecutionContract:
        return ExecutionContract(
            supported_commands={ExecuteCycleCommand},
            supported_events={"RequestAdded", "RequestRemoved"},
            supported_states={
                PipelineState.INITIALIZED,
                PipelineState.PREPARED,
                PipelineState.RUNNING,
                PipelineState.SYNCING,
                PipelineState.FINALIZED,
                PipelineState.CLEANED
            },
            supported_pipeline=self._pipeline.metadata,
            required_capabilities={"autoregressive_generation"},
            runtime_requirements={"mlx_lm": "any"}
        )

    def validate(self) -> BackendStatus:
        if self._runtime is None or self._runtime.engine is None:
            return BackendStatus(is_valid=False, errors=["Runtime or Engine is missing"])
        if not isinstance(self._runtime.engine, AutoregressiveExecutionEngine):
            return BackendStatus(is_valid=False, errors=["Engine must be an AutoregressiveExecutionEngine"])
        if self._runtime.engine.batch_generator is None:
            return BackendStatus(is_valid=False, errors=["BatchGenerator is not initialized"])
        return BackendStatus(is_valid=True)

    def plan(self) -> ExecutionPlan:
        steps = [stage.__class__.__name__ for stage in self._pipeline.stages]
        return ExecutionPlan(steps=steps, estimated_memory_bytes=0)

    def prepare(self, *args: Any, **kwargs: Any) -> Any:
        """
        Handle events like request additions/removals.
        """
        if "events" in kwargs:
            events = kwargs["events"]
            # Future: Handle RequestAdded, RequestRemoved here by mutating batch_generator state
            pass

    def execute(self, inputs: Any) -> Any:
        # Everything goes through pipeline.run()
        if hasattr(self._pipeline, "run"):
            return self._pipeline.run(inputs, self.runtime)
        return self._pipeline.execute(inputs, self.runtime)

    def synchronize(self) -> None:
        import mlx.core as mx
        mx.metal.synchronize()

    def finalize(self, *args: Any, **kwargs: Any) -> Any:
        return args[0] if args else None

    def cleanup(self) -> None:
        self._runtime = None

__all__ = [
    "AutoregressiveExecutionEngine",
    "AutoregressiveRuntime",
    "AutoregressivePipeline",
    "AutoregressiveBackend",
]
