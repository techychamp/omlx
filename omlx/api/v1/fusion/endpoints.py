from typing import Dict, Any, Optional
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionStatistics

class FusionAPI:
    """API for querying Fusion statistics and diagnostics."""

    def get_fusion_statistics(self, bundle: PlanningBundle) -> Optional[FusionStatistics]:
        if bundle.fusion_plan:
            return bundle.fusion_plan.statistics
        return None

    def get_fusion_diagnostics(self, bundle: PlanningBundle) -> tuple:
        if bundle.fusion_plan:
            return bundle.fusion_plan.diagnostics
        return tuple()
