from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio
from omlx.planner.compiler.transformation.artifacts import TransformationReport, TransformationStatistics, TransformationValidationReport

class TransformationStatisticsDTO(BaseModel):
    original_node_count: int
    transformed_node_count: int
    nodes_fused: int
    groups_realized: int

class TransformationDiagnosticDTO(BaseModel):
    level: str
    message: str
    node_id: Optional[str] = None

class TransformationValidationReportDTO(BaseModel):
    is_valid: bool
    diagnostics: list[TransformationDiagnosticDTO] = Field(default_factory=list)

class TransformationReportDTO(BaseModel):
    statistics: TransformationStatisticsDTO
    validation: TransformationValidationReportDTO

def convert_transformation_report(report: TransformationReport) -> TransformationReportDTO:
    stats = TransformationStatisticsDTO(
        original_node_count=report.statistics.original_node_count,
        transformed_node_count=report.statistics.transformed_node_count,
        nodes_fused=report.statistics.nodes_fused,
        groups_realized=report.statistics.groups_realized
    )

    diags = []
    for d in report.validation_report.diagnostics:
        diags.append(TransformationDiagnosticDTO(
            level=d.level,
            message=d.message,
            node_id=d.node_id if d.node_id else None
        ))

    val = TransformationValidationReportDTO(
        is_valid=report.validation_report.is_valid,
        diagnostics=diags
    )

    return TransformationReportDTO(
        statistics=stats,
        validation=val
    )
