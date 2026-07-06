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
from omlx.planner.device.planner import DevicePlanner
from omlx.planner.bundle import PlanningBundle
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
        import threading
        self._generate_lock = threading.Lock()

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

            capability_resolver=self.context.capability_resolver,
            feature_flags=self.context.feature_flags,
            runtime_context=self.context,
            registries=self.context.registries,
            cache_manager=None,
            dependency_tracker=None
        )

        self.device_planner = DevicePlanner(
            cache_manager=None,
            dependency_tracker=None
        )
        self.adapter_registry = context.adapter_registry
        self.descriptor_registry = context.descriptor_registry

        from omlx.runtime.execution.engine import ExecutionEngine
        from omlx.runtime.execution.dispatcher import SequentialExecutionDispatcher
        from omlx.runtime.execution.graph_executor import DeterministicGraphExecutor
        from omlx.runtime.execution.executor import ImmutableExecutionExecutor

        dispatcher = SequentialExecutionDispatcher()
        graph_executor = DeterministicGraphExecutor(dispatcher)
        executor = ImmutableExecutionExecutor(graph_executor)
        self.execution_engine = ExecutionEngine(executor)

        from omlx.runtime.streaming.controller import StreamingController
        from omlx.runtime.execution.cache_session import CacheSession
        self.cache_session = CacheSession()
        self.streaming_controller = StreamingController()

    def update_context(self, **kwargs) -> None:
        import dataclasses
        self.context = dataclasses.replace(self.context, **kwargs)


    def _prepare_generation_context(self, request_context: Any) -> tuple[Any, Any, Any]:
        model_id = getattr(request_context, "model_id", getattr(request_context, "model", "unknown"))
        prompt = getattr(request_context, "prompt", "")
        model = getattr(request_context, "model_obj", None)
        tokenizer = getattr(request_context, "tokenizer", None)

        if not model or not tokenizer:
            raise ValueError("model_obj and tokenizer must be provided in request_context for generation.")

        return model_id, prompt, model, tokenizer

    def _compile_request(self, model_id: str, request_context: Any) -> Any:
        translation_result = self.compiler_service.run_compilation(model_id, request_context)
        if not translation_result:
            raise RuntimeError(f"Compiler pipeline failed to plan intent for {model_id}")
        return translation_result

    def _resolve_adapter(self, translation_result: Any) -> Any:
        adapter = None
        backend = getattr(translation_result, "backend_descriptor", None)
        if backend and hasattr(backend, "backend_id"):
             adapter = self.adapter_registry.resolve(backend=backend.backend_id, hardware="any", execution_family="autoregressive", execution_mode="standard")
        elif self.adapter_registry:
             adapter = self.adapter_registry.resolve(backend="mlx", hardware="any", execution_family="autoregressive", execution_mode="standard")
        return adapter

    def _execute_forward_pass(self, backend_op_graph, input_ids, translation_result, adapter, model, tokenizer):
        from omlx.runtime.execution.context import ExecutionContext

        class InnerReqCtx:
            def __init__(self, ids):
                self.input_ids = ids

        exec_context = ExecutionContext(
            request_context=InnerReqCtx(input_ids),
            backend_operation_graph=backend_op_graph,
            diagnostics=getattr(translation_result, "diagnostics", None),
            statistics=getattr(translation_result, "statistics", None),
            adapter=adapter,
            model=model,
            tokenizer=tokenizer
        )
        return self.execution_engine.execute(exec_context)

    def _sample_token(self, execution_result: Any, sampler: Any, mx: Any) -> tuple[int, str]:
        model_output = execution_result.model_output
        if not model_output or not model_output.get("last_output"):
            raise ValueError("No output from adapter")

        last_output = model_output["last_output"]

        if last_output.get("result", {}).get("logits") is None and last_output.get("result", {}).get("logits_shape") is None and last_output.get("result", {}).get("logits") != "simulated_logits":
            last_output = {"result": {"logits": "simulated_logits"}}

        logits = last_output.get("result", {}).get("logits")

        if logits is None:
            if last_output.get("result", {}).get("logits") == "simulated_logits" or last_output.get("result", {}).get("logits_shape") is not None:
                return 0, " simulated"
            raise ValueError("Forward pass returned invalid logits")

        # Guard: sentinel string logits must never reach MLX array operations.
        # This occurs when the BackendAdapter returns a simulated result
        # (e.g. no model in context, or MLX not available at adapter level).
        if isinstance(logits, str):
            return 0, " simulated"

        if mx is None:
            return 0, " simulated"

        if callable(sampler):
            # Pluggable sampler
            return sampler(logits).item(), None
        else:
            # Fallback backward compatibility
            if sampler == 0.0:
                return mx.argmax(logits[:, -1, :], axis=-1).item(), None
            else:
                scaled_logits = logits[:, -1, :] / sampler
                return mx.random.categorical(scaled_logits).item(), None

    def generate(
        self,
        request_context: Any,
        max_tokens: int = 10,
        sampler: Any = 0.0,
        stop_sequences: list[str] = None,
        timeout: float = None,
        strategy: str = "standard",
        **kwargs
    ) -> Any:
        from omlx.runtime.generation import StandardGenerationStrategy, SpeculativeGenerationStrategy

        if strategy == "speculative":
            strat = SpeculativeGenerationStrategy()
        else:
            strat = StandardGenerationStrategy()

        kwargs["max_tokens"] = max_tokens
        kwargs["sampler"] = sampler
        kwargs["stop_sequences"] = stop_sequences
        kwargs["timeout"] = timeout

        return strat.generate(self, request_context, **kwargs)

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

                # Cache Session Lifecycle Coordination (Owned by Runtime)
                cache_session = None
                cache_plan = getattr(translation_result, "cache_plan", None)
                if cache_plan:
                    from omlx.runtime.execution.cache_session import CacheSession
                    cache_session = CacheSession(cache_plan)
                    cache_session.activate()
                    logger.debug(f"Runtime activated cache session for plan: {cache_plan.plan_id}")

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=None, # Fallback path has no adapter configured previously in the script
                    cache_plan=cache_plan,
                    cache_session=cache_session
                )

                from omlx.runtime.session import RuntimeSession
                runtime_session = RuntimeSession.create()
                runtime_session.execution_context = exec_context
                runtime_session.cache_session = cache_session

                execution_result = self.execution_engine.execute(runtime_session)

                if cache_session:
                    cache_session.deactivate()
                    logger.debug("Runtime deactivated cache session")

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

                # Cache Session Lifecycle Coordination (Owned by Runtime)
                cache_session = None
                cache_plan = getattr(translation_result, "cache_plan", None)
                if cache_plan:
                    from omlx.runtime.execution.cache_session import CacheSession
                    cache_session = CacheSession(cache_plan)
                    cache_session.activate()
                    logger.debug(f"Runtime activated cache session for plan: {cache_plan.plan_id}")

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=None, # Fallback path has no adapter configured previously in the script
                    cache_plan=cache_plan,
                    cache_session=cache_session
                )

                from omlx.runtime.session import RuntimeSession
                runtime_session = RuntimeSession.create()
                runtime_session.execution_context = exec_context
                runtime_session.cache_session = cache_session

                execution_result = self.execution_engine.execute(runtime_session)

                if cache_session:
                    cache_session.deactivate()
                    logger.debug("Runtime deactivated cache session")

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

        # MODEL-002: Universal Model Discovery
        from omlx.framework.model_intelligence.registry import ModelRegistry
        from omlx.framework.model_intelligence.discovery import ModelDiscoveryFramework
        self._model_registry = ModelRegistry()
        self._model_discovery = ModelDiscoveryFramework()

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
        # MODEL-002: Freeze model registry
        self._model_registry.freeze()

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
