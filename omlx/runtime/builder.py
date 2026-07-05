# SPDX-License-Identifier: Apache-2.0
"""
RuntimeBuilder and Composition Root implementation.
"""

from __future__ import annotations

import enum
import time
import logging
from dataclasses import dataclass, field
from omlx.capabilities import CapabilityResolver
from omlx.capabilities.descriptor import CapabilityDescriptor
from omlx.planner.planner import ExecutionPlanner, ExecutionPlan
from omlx.planner.ir.builder import IRBuilder
from omlx.planner.compiler import LoweringEngine
from omlx.planner.compiler.backend import AdapterRegistry, BackendDescriptorRegistry, MLXAdapter

from typing import Any, Optional
from omlx.runtime.execution import ExecutionEngine, ExecutionContext

from .context import RuntimeState
from .events import EventBus, RuntimeLifecycleEvent, Event, EventCategory
from .feature_flags import FeatureFlags

logger = logging.getLogger("omlx.runtime")


class RuntimeStateEnum(enum.Enum):
    CREATED = "created"
    BOOTSTRAPPING = "bootstrapping"
    INITIALIZING = "initializing"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class RuntimeContext:
    """Immutable snapshot of the runtime context."""
    settings: Any = None
    environment: Any = None
    hardware: Any = None
    capabilities: Any = None
    verification: Any = None
    capability_resolver: CapabilityResolver | None = None
    feature_flags: FeatureFlags = field(default_factory=FeatureFlags)
    registries: Any = None
    planner_references: Any = None
    startup_metadata: dict[str, Any] = field(default_factory=dict)
    version_info: dict[str, str] = field(default_factory=dict)
    adapter_registry: AdapterRegistry | None = None
    descriptor_registry: BackendDescriptorRegistry | None = None

    # Compiler Runtime Artifacts
    capability_descriptor: CapabilityDescriptor | None = None
    execution_plan: ExecutionPlan | None = None
    compiler_session: Any = None
    logical_ir: Any = None
    physical_ir: Any = None
    backend_operation_graph: Any = None
    compiler_diagnostics: Any = None
    translation_result: Any = None
    compiler_statistics: Any = None



class Runtime:
    """Central runtime object owning all subsystems.

    This replaces scattered singleton access in the Composition Root architecture.
    """

    def __init__(self, context: RuntimeContext) -> None:
        self.context = context
        self.state = RuntimeStateEnum.CREATED

        # Subsystems
        self.settings: Any = context.settings
        self.feature_flags: FeatureFlags = context.feature_flags
        self.registries: Any = None
        self.plugin_manager: Any = None
        self.verification_framework: Any = context.verification
        self.engine_pool: Any = None
        self.metrics: Any = None
        self.event_bus = EventBus()
        self.ir_builder = IRBuilder()
        self.lowering_engine = LoweringEngine()
        from omlx.runtime.compiler_service import RuntimeCompilerService
        self.compiler_service = RuntimeCompilerService(self)
        self.execution_planner = ExecutionPlanner(
            capability_resolver=context.capability_resolver,
            feature_flags=context.feature_flags,
            runtime_context=context,
            registries=context.registries
        )
        self.adapter_registry = context.adapter_registry
        self.descriptor_registry = context.descriptor_registry
        self.execution_engine = ExecutionEngine()

    def update_context(self, **kwargs) -> None:
        import dataclasses
        self.context = dataclasses.replace(self.context, **kwargs)

    def execute_request(self, request_context: Any) -> Any:
        """
        Execute an incoming request using the Compiler service and Execution Engine.
        """
        # Explicit legacy handling
        if self.feature_flags.LEGACY_RUNTIME_ENABLED and not self.feature_flags.COMPILER_RUNTIME_ENABLED:
            logger.debug("Falling back to legacy runtime execution.")
            # We don't have a legacy implementation in this file yet, so we raise NotImplementedError
            raise NotImplementedError("Legacy runtime execution is not yet implemented.")

        if self.feature_flags.COMPILER_RUNTIME_ENABLED:
            model_id = request_context.model

            # Use compiler to get graph directly instead of TranslationResult
            translation_result = self.compiler_service.run_compilation(model_id, request_context)
            if translation_result:
                logger.debug(f"Compiler pipeline successfully planned intent for {model_id}")

                # Execution Engine
                # We extract graph here, but future versions of CompilerService will return it directly
                backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None))

                # Determine backend adapter
                adapter = None
                backend = getattr(translation_result, "backend_descriptor", None)
                if backend and hasattr(backend, "backend_id"):
                     adapter = self.adapter_registry.resolve(backend=backend.backend_id, hardware="any", execution_family="autoregressive", execution_mode="standard")
                elif self.adapter_registry:
                     adapter = self.adapter_registry.resolve(backend="mlx", hardware="any", execution_family="autoregressive", execution_mode="standard")

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=adapter
                )

                execution_result = self.execution_engine.execute(exec_context)
                logger.debug(f"Execution Engine completed with status {execution_result.status}")

                return execution_result

        raise NotImplementedError("No execution path available for request.") # Assuming legacy handling occurs elsewhere since this method only had compiler paths

        if self.feature_flags.COMPILER_RUNTIME_ENABLED:
            model_id = request_context.model
            translation_result = self.compiler_service.run_compilation(model_id, request_context)
            if translation_result:
                logger.debug(f"Compiler pipeline successfully planned intent for {model_id}")

                # Execution Engine
                backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None))

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None)
                )

                execution_result = self.execution_engine.execute(exec_context)
                logger.debug(f"Execution Engine completed with status {execution_result.status}")

                return execution_result

        return None

    def transition(self, new_state: RuntimeStateEnum) -> None:
        """Safely transition lifecycle states."""
        # Add basic state machine validation here if needed
        self.state = new_state
        logger.debug(f"Runtime state transition: {self.state.value}")


class RuntimeBuilder:
    """Builder for assembling the Runtime object."""

    def __init__(self) -> None:
        self._settings = None
        self._feature_flags = FeatureFlags.from_env()
        self._verification = None
        self._capability_resolver = CapabilityResolver()
        self._engine_pool = None
        self._adapter_registry = AdapterRegistry()
        self._descriptor_registry = BackendDescriptorRegistry()

        # Register default MLX adapter and descriptor
        mlx_adapter = MLXAdapter()
        self._descriptor_registry.register("mlx", mlx_adapter.descriptor)
        
        # Pre-register combinations for reference MLX execution
        for family in ("autoregressive", "diffusion", "embedding", "speculative"):
            for mode in ("standard", "streaming"):
                for hardware in ("gpu", "metal", "apple_silicon", "any"):
                    self._adapter_registry.register(
                        backend="mlx",
                        hardware=hardware,
                        execution_family=family,
                        execution_mode=mode,
                        adapter=mlx_adapter
                    )

    def with_settings(self, settings: Any) -> RuntimeBuilder:
        self._settings = settings
        return self

    def with_feature_flags(self, feature_flags: FeatureFlags) -> RuntimeBuilder:
        self._feature_flags = feature_flags
        return self

    def with_verification(self, verification: Any) -> RuntimeBuilder:
        self._verification = verification
        return self

    def with_engine_pool(self, engine_pool: Any) -> RuntimeBuilder:
        self._engine_pool = engine_pool
        return self


    def build(self) -> Runtime:
        """Construct the immutable context and wire up the Runtime."""
        # Lock registries before startup
        self._adapter_registry.lock()
        self._descriptor_registry.lock()

        context = RuntimeContext(
            settings=self._settings,
            feature_flags=self._feature_flags,
            verification=self._verification,
            capability_resolver=self._capability_resolver,
            startup_metadata={"start_time": time.time()},
            adapter_registry=self._adapter_registry,
            descriptor_registry=self._descriptor_registry
        )

        runtime = Runtime(context)
        runtime.engine_pool = self._engine_pool

        # Publish starting event
        runtime.event_bus.publish(Event(
            type=RuntimeLifecycleEvent.RUNTIME_STARTING,
            category=EventCategory.RUNTIME,
            source="RuntimeBuilder"
        ))

        runtime.transition(RuntimeStateEnum.BOOTSTRAPPING)

        # In a full implementation, registries and plugin manager would be initialized here

        return runtime
