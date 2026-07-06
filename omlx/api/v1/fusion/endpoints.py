from typing import Optional
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.domains.fusion.artifacts import FusionStatistics
from omlx.planner.compiler.transformation.artifacts import TransformationReport
from omlx.api.v1.fusion.transformation import TransformationReportDTO, convert_transformation_report

class FusionAPIEndpoints:
    def __init__(self):
        self._transformation_reports = {}

    def get_fusion_statistics(self, bundle: PlanningBundle) -> Optional[FusionStatistics]:
        if bundle and bundle.fusion_plan:
            return bundle.fusion_plan.statistics
        return None

    def get_fusion_diagnostics(self, bundle: PlanningBundle) -> tuple:
        if bundle and bundle.fusion_plan:
            return bundle.fusion_plan.diagnostics
        return ()

    def get_transformation_report(self, request_id: str) -> Optional[TransformationReportDTO]:
        """Retrieves the transformation report for a given request."""
        report = self._transformation_reports.get(request_id)
        if report:
             return convert_transformation_report(report)
        return None

    def record_transformation_report(self, request_id: str, report: TransformationReport):
        """Internal method to record transformation reports."""
        self._transformation_reports[request_id] = report
