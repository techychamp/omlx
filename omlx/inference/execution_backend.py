# SPDX-License-Identifier: Apache-2.0
"""
Execution backend and pipeline interfaces for OMLX inference.
"""

from __future__ import annotations

import time
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Protocol, runtime_checkable


class ExecutionCommand(ABC):
    """Base class for all execution commands."""
    pass


@dataclass
class ExecuteCycleCommand(ExecutionCommand):
    """Command to execute a single cycle/step of inference."""
    inputs: Any


class PipelineState(Enum):
    INITIALIZED = auto()
    PREPARED = auto()
    RUNNING = auto()
    SYNCING = auto()
    FINALIZED = auto()
    CLEANED = auto()


class InvalidPipelineTransition(Exception):
    """Raised when an invalid state transition is attempted on a pipeline."""
    pass


@dataclass
class PipelineMetadata:
    supports_streaming: bool = False
    supports_speculation: bool = False
    supports_diffusion: bool = False
    supports_bidirectional: bool = False
    supports_shared_cache: bool = False


@dataclass
class PipelineMetrics:
    stage_timings: dict[str, float] = field(default_factory=dict)
    total_time: float = 0.0


@dataclass
class ExecutionContract:
    supported_commands: set[type[ExecutionCommand]]
    supported_events: set[str]
    supported_states: set[PipelineState]
    supported_pipeline: PipelineMetadata
    required_capabilities: set[str]
    runtime_requirements: dict[str, Any]


@dataclass
class BackendStatus:
    is_valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    steps: list[str]
    estimated_memory_bytes: int = 0


@runtime_checkable
class ExecutionEngine(Protocol):
    """The lowest-level execution engine (e.g., wrappers around MLX, Torch)."""
    pass


@runtime_checkable
class ExecutionRuntime(Protocol):
    """Abstracts the underlying compute platform (MLX, Torch, Metal) for a backend."""
    @property
    def engine(self) -> ExecutionEngine:
        """Get the underlying execution engine."""
        ...


@runtime_checkable
class ExecutionStage(Protocol):
    """A modular block of execution within a pipeline (e.g., Prefill, Forward, Sample)."""
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        """Execute this stage given the inputs and the runtime."""
        ...


class ExtractCacheStage:
    """A pipeline stage responsible for extracting or managing cache states."""
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        # cache extraction logic
        return inputs


class ExecutionPipeline:
    """Manages an ordered sequence of ExecutionStages."""
    def __init__(self, stages: list[ExecutionStage], metadata: PipelineMetadata | None = None) -> None:
        self.stages = stages
        self._metadata = metadata or PipelineMetadata()
        self._state = PipelineState.INITIALIZED
        self._metrics = PipelineMetrics()

    @property
    def metadata(self) -> PipelineMetadata:
        return self._metadata

    @property
    def state(self) -> PipelineState:
        return self._state

    @property
    def metrics(self) -> PipelineMetrics:
        return self._metrics

    def transition_to(self, new_state: PipelineState) -> None:
        valid_transitions = {
            PipelineState.INITIALIZED: {PipelineState.PREPARED, PipelineState.RUNNING, PipelineState.CLEANED},
            PipelineState.PREPARED: {PipelineState.RUNNING, PipelineState.CLEANED},
            PipelineState.RUNNING: {PipelineState.SYNCING, PipelineState.FINALIZED, PipelineState.CLEANED},
            PipelineState.SYNCING: {PipelineState.RUNNING, PipelineState.FINALIZED, PipelineState.CLEANED},
            PipelineState.FINALIZED: {PipelineState.PREPARED, PipelineState.RUNNING, PipelineState.CLEANED},
            PipelineState.CLEANED: {PipelineState.INITIALIZED},
        }
        if new_state not in valid_transitions[self._state]:
            raise InvalidPipelineTransition(f"Cannot transition from {self._state} to {new_state}")
        self._state = new_state

    def describe(self) -> str:
        """Returns a string description of the stages in the pipeline."""
        if not self.stages:
            return "Empty Pipeline"
        return " -> ".join(stage.__class__.__name__ for stage in self.stages)

    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        """Run the inputs sequentially through all stages."""
        self.transition_to(PipelineState.RUNNING)
        current_state = inputs
        start_time = time.time()
        for stage in self.stages:
            stage_start = time.time()
            current_state = stage.execute(current_state, runtime)
            stage_end = time.time()
            stage_name = stage.__class__.__name__
            self._metrics.stage_timings[stage_name] = stage_end - stage_start
        self._metrics.total_time = time.time() - start_time
        self.transition_to(PipelineState.FINALIZED)
        return current_state


class PipelineBuilder:
    """Dynamically composes ExecutionStages into an ExecutionPipeline."""
    def __init__(self) -> None:
        self._stages: list[ExecutionStage] = []
        self._metadata = PipelineMetadata()

    def add_stage(self, stage: ExecutionStage) -> 'PipelineBuilder':
        """Append a stage to the pipeline."""
        self._stages.append(stage)
        return self
        
    def set_metadata(self, metadata: PipelineMetadata) -> 'PipelineBuilder':
        """Set pipeline metadata."""
        self._metadata = metadata
        return self

    def build(self) -> ExecutionPipeline:
        """Construct the ExecutionPipeline."""
        return ExecutionPipeline(list(self._stages), self._metadata)


@runtime_checkable
class ExecutionBackend(Protocol):
    """
    The highest-level execution abstraction.
    
    Responsible for executing a specific algorithm (Autoregressive, Diffusion, etc.)
    using an underlying ExecutionPipeline and ExecutionRuntime.
    """
    
    @property
    def runtime(self) -> ExecutionRuntime:
        """The runtime underlying this backend."""
        ...
        
    @property
    def pipeline(self) -> ExecutionPipeline:
        """The execution pipeline for this backend."""
        ...
        
    @property
    def contract(self) -> ExecutionContract:
        """Execution contract specifying capabilities."""
        ...

    def prepare(self, *args: Any, **kwargs: Any) -> Any:
        """Prepare inputs, caches, and memory for execution."""
        ...

    def execute(self, inputs: Any) -> Any:
        """Execute the pipeline with the given inputs."""
        ...

    def synchronize(self) -> None:
        """Synchronize execution streams (e.g., metal stream synchronization)."""
        ...

    def finalize(self, *args: Any, **kwargs: Any) -> Any:
        """Process output results and finalize the execution step."""
        ...

    def cleanup(self) -> None:
        """Release resources, clear caches, and shut down the backend safely."""
        ...
        
    def validate(self) -> BackendStatus:
        """Validate the backend configuration and state."""
        ...
        
    def plan(self) -> ExecutionPlan:
        """Plan the execution steps and estimate resources."""
        ...

__all__ = [
    "ExecutionCommand",
    "ExecuteCycleCommand",
    "PipelineState",
    "InvalidPipelineTransition",
    "PipelineMetadata",
    "PipelineMetrics",
    "ExecutionContract",
    "BackendStatus",
    "ExecutionPlan",
    "ExecutionEngine",
    "ExecutionRuntime",
    "ExecutionStage",
    "ExtractCacheStage",
    "ExecutionPipeline",
    "PipelineBuilder",
    "ExecutionBackend",
]
