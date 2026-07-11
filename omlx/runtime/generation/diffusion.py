from typing import Any, Dict, Optional
from .strategy import GenerationStrategy
from omlx.planner.domains.diffusion import DiffusionPlan, DiffusionStatistics

class DiffusionGenerationStrategy(GenerationStrategy):
    """
    GenerationStrategy that orchestrates diffusion execution.
    It relies on the ExecutionEngine for executing tensor operations.
    """

    def __init__(self, plan: Optional[DiffusionPlan] = None):
        self.plan = plan

    @property
    def strategy_intent(self) -> str:
        return "diffusion"


    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:
        """
        Orchestrates diffusion by coordinating timesteps and denoising.
        The actual execution happens in the runtime/engine.
        """
        if not self.plan:
            raise ValueError("DiffusionPlan must be set for DiffusionGenerationStrategy")

        from omlx.runtime.observability import get_observer
        from omlx.runtime.execution.context import ExecutionContext
        from omlx.runtime.session import RuntimeSession
        import uuid

        # Canonical compiler pipeline
        translation_result = runtime.compiler_service.run_compilation(request_context.model, request_context)
        adapter = runtime.adapter_registry.resolve(translation_result)

        # Retrieve the realized diffusion graph directly from the compiler artifact
        diffusion_graph = getattr(translation_result, "diffusion_execution_graph", None)

        # Build context and session
        context = ExecutionContext(
            backend_operation_graph=translation_result.backend_graph,
            diffusion_execution_graph=diffusion_graph,
            adapter=adapter,
            request_context=request_context
        )

        session = RuntimeSession(
            session_id=str(uuid.uuid4()),
            execution_context=context
        )

        # Execute natively
        result = runtime.execution_engine.execute(session)

        # Retrieve diffusion report
        diffusion_report = get_observer().artifact_tracker.get("DiffusionExecutionReport")

        return {
            "status": "success",
            "statistics": DiffusionStatistics(
                planning_latency_ms=0.0, # TODO: Real statistics to be extracted from execution report
                iteration_statistics={"total_steps": len(self.plan.timestep_schedule)},
                timestep_statistics={"schedule": self.plan.timestep_schedule}
            ),
            "diffusion_report": diffusion_report,
            "model_output": result.model_output
        }

    def get_cache_policy(self) -> dict:
        return {"use_cache": False, "policy": "diffusion_no_cache"}
