"""
Intelligent Backend Evaluation, Telemetry, and Adaptive Selection framework.
"""
from .evaluator import BackendEvaluator
from .cost_model import BackendCostModel
from .telemetry import BackendTelemetry, BackendTelemetrySummary
from .benchmark import BackendBenchmarkProfile
from .discovery import BackendCapabilityDiscovery
from .reports import (
    BackendEvaluationReport,
    BackendSelectionReport,
    BackendRecommendationReport,
    BackendCostReport,
    BackendCapabilityReport
)

__all__ = [
    "BackendEvaluator",
    "BackendCostModel",
    "BackendTelemetry",
    "BackendTelemetrySummary",
    "BackendBenchmarkProfile",
    "BackendCapabilityDiscovery",
    "BackendEvaluationReport",
    "BackendSelectionReport",
    "BackendRecommendationReport",
    "BackendCostReport",
    "BackendCapabilityReport"
]
