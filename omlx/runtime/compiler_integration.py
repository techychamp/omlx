# SPDX-License-Identifier: Apache-2.0
"""
Orchestrates the OMLX Compiler Pipeline within the runtime.
Does not own its dependencies; dependencies are injected via the Runtime instance.
"""
from typing import Any, Optional
import time
import logging

from omlx.planner.compiler.backend.adapter import TranslationResult
from omlx.planner.ir.builder import IRBuilder

logger = logging.getLogger("omlx.compiler_integration")

class CompilerPipelineRunner:
    """
    Executes the compiler pipeline on an incoming request to generate
    a TranslationResult, preserving diagnostics and analytics.
    """
    def __init__(self, runtime: Any):
        """
        Initialize with an injected Runtime object.
        """
        self.runtime = runtime

    def run_pipeline(self, model_id: str, request_context: Any = None) -> Optional[TranslationResult]:
        from omlx.runtime.observability import get_observer
        flags = self.runtime.feature_flags

        if not flags.COMPILER_RUNTIME_PIPELINE_ENABLED:
            return None

        start_time = time.time()
        logger.debug(f"Starting compiler pipeline for model {model_id}")

        with get_observer().observe_phase("Compilation", "CompilerPipeline", "run_pipeline"):
            # 1. Capability Resolution
            descriptor = None
            if flags.CAPABILITY_RUNTIME_ENABLED:
                with get_observer().observe_phase("Compilation", "CapabilityResolver", "resolve"):
                    try:
                        descriptor = self.runtime.context.capability_resolver.resolve(model_descriptor={"model_id": model_id})
                        get_observer().track_artifact("CapabilityDescriptor", descriptor)
                        logger.debug(f"Capability resolution completed for {model_id}")
                    except Exception as e:
                        logger.error(f"Capability resolution failed: {e}", exc_info=True)
                        get_observer().add_diagnostic(f"Capability resolution failed: {e}")
                        return None

            if descriptor is None:
                return None

            # 2. Execution Planning
            plan = None
            if flags.PLANNER_RUNTIME_ENABLED:
                with get_observer().observe_phase("Compilation", "ExecutionPlanner", "plan"):
                    try:
                        plan = self.runtime.execution_planner.plan(descriptor)
                        get_observer().track_artifact("ExecutionPlan", plan)
                        logger.debug(f"Execution planning completed for {model_id}")
                    except Exception as e:
                        logger.error(f"Execution planning failed: {e}", exc_info=True)
                        get_observer().add_diagnostic(f"Execution planning failed: {e}")
                        return None

            if plan is None:
                return None

            # 3. Logical IR Generation & Lowering
            physical_ir = None
            if flags.LOWERING_RUNTIME_ENABLED:
                with get_observer().observe_phase("Compilation", "LoweringEngine", "lower"):
                    try:
                        logical_ir = self.runtime.ir_builder.build(plan)
                        get_observer().track_artifact("LogicalIR", logical_ir)
                        physical_ir = self.runtime.lowering_engine.lower(logical_ir)
                        get_observer().track_artifact("PhysicalIR", physical_ir)
                        logger.debug(f"IR lowering completed for {model_id}")
                    except Exception as e:
                        logger.error(f"IR lowering failed: {e}", exc_info=True)
                        get_observer().add_diagnostic(f"IR lowering failed: {e}")
                        return None

            if physical_ir is None:
                return None

            # 4. Adapter Translation
            translation_result = None
            if flags.ADAPTER_RUNTIME_ENABLED:
                with get_observer().observe_phase("Compilation", "AdapterRegistry", "translate"):
                    try:
                        hardware = plan.hardware_requirements[0] if plan.hardware_requirements else "any"
                        execution_family = plan.execution_family if isinstance(plan.execution_family, str) else str(plan.execution_family.value)
                        execution_mode = plan.execution_mode

                        adapter = self.runtime.adapter_registry.resolve(
                            backend="mlx",
                            hardware=hardware,
                            execution_family=execution_family,
                            execution_mode=execution_mode
                        )

                        if adapter:
                            translation_result = adapter.translate(physical_ir)
                            get_observer().track_artifact("TranslationResult", translation_result)
                            logger.debug(f"Adapter translation completed for {model_id}")
                        else:
                            logger.warning(f"No adapter found for backend=mlx, family={plan.execution_family}")
                            get_observer().add_diagnostic(f"No adapter found for backend=mlx, family={plan.execution_family}")
                            return None
                    except Exception as e:
                        logger.error(f"Adapter translation failed: {e}", exc_info=True)
                        get_observer().add_diagnostic(f"Adapter translation failed: {e}")
                        return None

            total_time = (time.time() - start_time) * 1000
            logger.debug(f"Compiler pipeline finished for {model_id} in {total_time:.2f}ms")

            if flags.COMPILER_CONTEXT_ENABLED:
                backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None)) if translation_result else None
                if backend_op_graph:
                    get_observer().track_artifact("BackendOperationGraph", backend_op_graph)
                self.runtime.update_context(
                    capability_descriptor=descriptor,
                    execution_plan=plan,
                    logical_ir=logical_ir if 'logical_ir' in locals() else None,
                    physical_ir=physical_ir,
                    translation_result=translation_result,
                    backend_operation_graph=backend_op_graph
                )

            return translation_result0
"""
Orchestrates the OMLX Compiler Pipeline within the runtime.
Does not own its dependencies; dependencies are injected via the Runtime instance.
"""
from typing import Any, Optional
import time
import logging

from omlx.planner.compiler.backend.adapter import TranslationResult
from omlx.planner.ir.builder import IRBuilder

logger = logging.getLogger("omlx.compiler_integration")

class CompilerPipelineRunner:
    """
    Executes the compiler pipeline on an incoming request to generate
    a TranslationResult, preserving diagnostics and analytics.
    """
    def __init__(self, runtime: Any):
        """
        Initialize with an injected Runtime object.
        """
        self.runtime = runtime

    def run_pipeline(self, model_id: str, request_context: Any = None) -> Optional[TranslationResult]:
        """
        Run the execution preparation pipeline stages based on feature flags.
        Returns the final TranslationResult if adapter translation succeeds, else None.
        """
        flags = self.runtime.feature_flags

        if not flags.COMPILER_RUNTIME_PIPELINE_ENABLED:
            return None

        start_time = time.time()
        logger.debug(f"Starting compiler pipeline for model {model_id}")

        # 1. Capability Resolution
        descriptor = None
        if flags.CAPABILITY_RUNTIME_ENABLED:
            try:
                descriptor = self.runtime.context.capability_resolver.resolve(model_descriptor={"model_id": model_id})
                logger.debug(f"Capability resolution completed for {model_id}")
            except Exception as e:
                logger.error(f"Capability resolution failed: {e}", exc_info=True)
                return None

        if descriptor is None:
            return None

        # 2. Execution Planning
        plan = None
        if flags.PLANNER_RUNTIME_ENABLED:
            try:
                plan = self.runtime.execution_planner.plan(descriptor)
                logger.debug(f"Execution planning completed for {model_id}")
            except Exception as e:
                logger.error(f"Execution planning failed: {e}", exc_info=True)
                return None

        if plan is None:
            return None

        # 3. Logical IR Generation & Lowering
        physical_ir = None
        if flags.LOWERING_RUNTIME_ENABLED:
            try:
                logical_ir = self.runtime.ir_builder.build(plan)
                physical_ir = self.runtime.lowering_engine.lower(logical_ir)
                logger.debug(f"IR lowering completed for {model_id}")
            except Exception as e:
                logger.error(f"IR lowering failed: {e}", exc_info=True)
                return None

        if physical_ir is None:
            return None

        # 4. Adapter Translation
        translation_result = None
        if flags.ADAPTER_RUNTIME_ENABLED:
            try:
                # Resolve backend from plan.
                # NOTE: plan.execution_backend holds the *logical* execution algorithm name
                # (e.g. "autoregressive", "speculative"), NOT the hardware backend ID.
                # The hardware backend registered in AdapterRegistry is "mlx" for the
                # primary compiler path. We use plan.execution_family and plan.execution_mode
                # to route into the correct variant within the mlx backend registrations.
                hardware = plan.hardware_requirements[0] if plan.hardware_requirements else "any"
                execution_family = plan.execution_family if isinstance(plan.execution_family, str) else str(plan.execution_family.value)
                execution_mode = plan.execution_mode

                adapter = self.runtime.adapter_registry.resolve(
                    backend="mlx",
                    hardware=hardware,
                    execution_family=execution_family,
                    execution_mode=execution_mode
                )

                if adapter:
                    # Translate Physical IR to Backend Operation Graph
                    translation_result = adapter.translate(physical_ir)
                    logger.debug(f"Adapter translation completed for {model_id}")
                else:
                    logger.warning(f"No adapter found for backend={backend}, family={plan.execution_family}")
                    return None
            except Exception as e:
                logger.error(f"Adapter translation failed: {e}", exc_info=True)
                return None

        total_time = (time.time() - start_time) * 1000
        logger.debug(f"Compiler pipeline finished for {model_id} in {total_time:.2f}ms")

        if flags.COMPILER_CONTEXT_ENABLED:
            # Also store the BackendOperationGraph explicitly if available
            backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None)) if translation_result else None
            self.runtime.update_context(
                capability_descriptor=descriptor,
                execution_plan=plan,
                logical_ir=logical_ir if 'logical_ir' in locals() else None,
                physical_ir=physical_ir,
                translation_result=translation_result,
                backend_operation_graph=backend_op_graph
            )

        return translation_result
