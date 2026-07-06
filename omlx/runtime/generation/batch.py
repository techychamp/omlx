from typing import Any
from omlx.runtime.generation.strategy import GenerationStrategy
from omlx.planner.domains.batch.artifacts import BatchPlan

class BatchGenerationStrategy(GenerationStrategy):
    @property
    def strategy_intent(self) -> str:
        return "batch"

    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:
        return "batch_execution"

    def get_cache_policy(self) -> dict:
        return {"use_cache": True, "policy": "batch_optimized"}
