from ...backend.descriptor import BackendDescriptor
from .cost_model import BackendCostModel
from .discovery import BackendCapabilityDiscovery
from .benchmark import BackendBenchmarkProfile
from .reports import BackendEvaluationReport

class BackendEvaluator:
    """Evaluates backend suitability, cost, and capabilities without executing it."""

    @staticmethod
    def evaluate(
        descriptor: BackendDescriptor,
        benchmark: BackendBenchmarkProfile | None = None
    ) -> BackendEvaluationReport:
        """Perform a full evaluation of a backend."""
        cost_report = BackendCostModel.estimate_cost(descriptor, benchmark)
        capability_report = BackendCapabilityDiscovery.discover(descriptor)

        # Heuristics for scoring
        hardware_fit_score = 1.0 if any(
            "gpu" in hc.lower() or "metal" in hc.lower() or "cuda" in hc.lower()
            for hc in descriptor.hardware_capabilities
        ) else 0.5

        compatibility_score = 1.0 if capability_report.supported_execution_families else 0.0
        optimization_support_score = min(1.0, len(capability_report.supported_optimization_phases) / 5.0)

        suitability_score = (
            hardware_fit_score * 0.4 +
            compatibility_score * 0.4 +
            optimization_support_score * 0.2
        )

        is_suitable = suitability_score > 0.3
        rejection_reasons = [] if is_suitable else ["Low suitability score"]

        return BackendEvaluationReport(
            backend_id=descriptor.backend_id,
            suitability_score=suitability_score,
            compatibility_score=compatibility_score,
            hardware_fit_score=hardware_fit_score,
            optimization_support_score=optimization_support_score,
            cost_report=cost_report,
            capability_report=capability_report,
            is_suitable=is_suitable,
            rejection_reasons=tuple(rejection_reasons)
        )