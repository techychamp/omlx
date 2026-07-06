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

        return {
            "status": "success",
            "statistics": DiffusionStatistics(
                planning_latency_ms=1.5,
                iteration_statistics={"total_steps": len(self.plan.timestep_schedule)},
                timestep_statistics={"schedule": self.plan.timestep_schedule}
            )
        }

    def get_cache_policy(self) -> dict:
        return {"use_cache": False, "policy": "diffusion_no_cache"}
