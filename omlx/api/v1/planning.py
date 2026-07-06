from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.runtime.feature_flags import FeatureFlags
from omlx.api.v1.exceptions import PlanningError
import logging

logger = logging.getLogger("omlx.api.v1.planning")

class PlanningStageSummary(BaseModel, frozen=True):
    stage_name: str
    description: str
    operations_count: int = 0

class PlanningResult(BaseModel, frozen=True):
    success: bool = True
    plan_id: str = "plan-123"
    stages: List[PlanningStageSummary] = Field(default_factory=list)
    diagnostics: Dict[str, str] = Field(default_factory=dict)

class PlanningRequest(BaseModel, frozen=True):
    capabilities: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    model_id: Optional[str] = None

class Planner:
    def __init__(self):
        self._planner = ExecutionPlanner(
            capability_resolver=CapabilityResolver(),
            feature_flags=FeatureFlags.from_env()
        )

    async def plan_async(self, request: PlanningRequest) -> PlanningResult:
        return await asyncio.to_thread(self.plan, request)

    def plan(self, request: PlanningRequest) -> PlanningResult:
        try:
            logger.info(f"Formulating execution plan. Requested capabilities: {request.capabilities}")

            # Map required string capabilities to execution features/hints
            hints = request.constraints.copy()
            hints["requested_capabilities"] = tuple(request.capabilities)

            descriptor = CapabilityDescriptor(
                execution_family=ExecutionFamily.AUTOREGRESSIVE,
                supports_streaming=True,
                supports_speculative=False,
                supports_verification=False,
                cache_layout="kv_cache",
                execution_hints=hints,
                hardware_requirements=("apple_silicon",)
            )

            plan_obj = self._planner.plan(descriptor)

            stages = [
                PlanningStageSummary(stage_name="capability_resolution", description="Resolved requested capabilities", operations_count=len(request.capabilities)),
                PlanningStageSummary(stage_name="execution_planning", description="Generated execution plan", operations_count=len(plan_obj.optimization_passes))
            ]
            return PlanningResult(success=True, stages=stages)
        except Exception as e:
            raise PlanningError(f"Planning failed: {str(e)}") from e

class PlanningRequestBuilder:
    def __init__(self):
        self._capabilities: List[str] = []
        self._constraints: Dict[str, Any] = {}
        self._model_id: Optional[str] = None

    def require_capability(self, capability: str) -> 'PlanningRequestBuilder':
        self._capabilities.append(capability)
        return self

    def with_constraint(self, key: str, value: Any) -> 'PlanningRequestBuilder':
        self._constraints[key] = value
        return self

    def with_model(self, model_id: str) -> 'PlanningRequestBuilder':
        self._model_id = model_id
        return self

    def build_request(self) -> PlanningRequest:
        return PlanningRequest(
            capabilities=self._capabilities,
            constraints=self._constraints,
            model_id=self._model_id
        )

    def build(self) -> Planner:
        return Planner()
