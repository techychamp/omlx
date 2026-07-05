# SPDX-License-Identifier: Apache-2.0
"""
Backend Selection Framework Orchestrator.
"""
import time
from typing import List, Tuple
from types import MappingProxyType
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import CapabilityDescriptor
from ..descriptor import BackendDescriptorRegistry
from .policy import ExecutionPolicy, BackendSelectionPolicy
from ..evaluation.strategy_registry import BackendPolicyStrategyRegistry
from .evaluation import BackendEvaluationReport
from .compatibility import CompatibilityChecker, CompatibilityReport
from .negotiation import BackendNegotiator, NegotiationDiagnostics
from .fallback import FallbackPlan, FallbackNode
from .diagnostics import BackendSelectionDiagnostics
from ..evaluation.evaluator import BackendEvaluator
from ..evaluation.reports import BackendSelectionReport, BackendRecommendationReport, BackendEvaluationReport as DetailedBackendEvaluationReport
from ..evaluation.telemetry import BackendTelemetry, BackendTelemetrySummary

class BackendSelectionFramework:
    def __init__(self, registry: BackendDescriptorRegistry, strategy_registry: BackendPolicyStrategyRegistry | None = None, telemetry: BackendTelemetry | None = None) -> None:
        self.registry = registry
        self.strategy_registry = strategy_registry or BackendPolicyStrategyRegistry()
        self.telemetry = telemetry or BackendTelemetry()

    def select_backend(
        self,
        plan: ExecutionPlan,
        cap_desc: CapabilityDescriptor,
        policy: ExecutionPolicy,
        candidate_ids: List[str]
    ) -> Tuple[str, BackendSelectionDiagnostics]:
        timestamp = time.time()

        evaluations = {}
        detailed_evaluations = {}
        compatibility_reports = {}
        negotiations = {}
        fallback_nodes = []

        selected_backend = ""
        best_score = -1.0

        strategy = self.strategy_registry.resolve(policy.selection_policy.name) if self.strategy_registry else None

        for backend_id in candidate_ids:
            if not self.registry.exists(backend_id):
                continue

            backend_desc = self.registry.get(backend_id)

            # 1. Compatibility
            comp_report = CompatibilityChecker.check_compatibility(plan, backend_desc, cap_desc, policy)
            compatibility_reports[backend_id] = comp_report

            # 2. Negotiation
            neg_diag = BackendNegotiator.negotiate(plan, backend_desc, cap_desc)
            negotiations[backend_id] = neg_diag

            # 3. Evaluation (Detailed)
            detailed_eval = BackendEvaluator.evaluate(backend_desc)
            detailed_evaluations[backend_id] = detailed_eval

            # Map to legacy eval_report for compatibility
            eval_report = BackendEvaluationReport(
                backend_id=backend_id,
                is_compatible=comp_report.is_compatible,
                estimated_latency_ms=detailed_eval.cost_report.estimated_latency_ms,
                estimated_memory_mb=detailed_eval.cost_report.estimated_peak_memory_mb,
                estimated_throughput_tps=detailed_eval.cost_report.estimated_throughput_tokens_per_sec,
                estimated_startup_cost_ms=detailed_eval.cost_report.estimated_startup_time_ms,
                cache_compatibility_score=detailed_eval.cost_report.cache_efficiency_score,
                hardware_utilization_score=detailed_eval.cost_report.hardware_utilization_score,
                diagnostics=MappingProxyType({"comp_warnings": comp_report.warnings})
            )
            evaluations[backend_id] = eval_report

            fallback_nodes.append(
                FallbackNode(
                    backend_id=backend_id,
                    is_compatible=comp_report.is_compatible,
                    reasons=comp_report.reasons
                )
            )

            if comp_report.is_compatible:
                # Use strategy pattern to evaluate score
                score = strategy.score(eval_report)

                # Tiebreaker using alphabetical ID to enforce determinism
                if score > best_score or (score == best_score and (not selected_backend or backend_id < selected_backend)):
                    best_score = score
                    selected_backend = backend_id

        # Apply developer override if specified and compatible
        if policy.selected_backend and policy.selected_backend in compatibility_reports and compatibility_reports[policy.selected_backend].is_compatible:
             selected_backend = policy.selected_backend

        fallback_plan = FallbackPlan(
            primary_backend=policy.selected_backend if policy.selected_backend else selected_backend,
            selected_backend=selected_backend,
            nodes=tuple(fallback_nodes),
            is_successful=bool(selected_backend)
        )

        evaluation_time_ms = (time.time() - timestamp) * 1000.0

        telemetry_summary = None
        selection_report = None
        if selected_backend:
            sel_eval = detailed_evaluations[selected_backend]
            telemetry_summary = BackendTelemetrySummary(
                selection_reason=policy.selection_reason,
                policy_applied=policy.selection_policy.name,
                estimated_latency_ms=sel_eval.cost_report.estimated_latency_ms,
                estimated_peak_memory_mb=sel_eval.cost_report.estimated_peak_memory_mb,
                estimated_throughput_tokens_per_sec=sel_eval.cost_report.estimated_throughput_tokens_per_sec,
                capability_usage=sel_eval.capability_report.supported_optimization_phases,
                fallback_usage=tuple(n.backend_id for n in fallback_plan.nodes)
            )
            self.telemetry.record_selection(selected_backend, telemetry_summary, evaluation_time_ms)

            recommendations = []
            for bid, deval in detailed_evaluations.items():
                if deval.is_suitable:
                    recommendations.append(BackendRecommendationReport(
                        backend_id=bid,
                        recommendation_score=deval.suitability_score,
                        reasons=deval.rejection_reasons
                    ))

            selection_report = BackendSelectionReport(
                selected_backend_id=selected_backend,
                policy_applied=policy.selection_policy.name,
                evaluations=MappingProxyType(detailed_evaluations),
                recommendations=tuple(recommendations),
                fallback_plan=tuple(n.backend_id for n in fallback_plan.nodes)
            )

        diagnostics = BackendSelectionDiagnostics(
            timestamp=timestamp,
            candidate_backends=tuple(candidate_ids),
            evaluations=MappingProxyType(evaluations),
            compatibility_reports=MappingProxyType(compatibility_reports),
            negotiations=MappingProxyType(negotiations),
            fallback_plan=fallback_plan,
            selected_backend=selected_backend,
            detailed_evaluations=MappingProxyType(detailed_evaluations),
            telemetry_summary=telemetry_summary,
            selection_report=selection_report
        )

        return selected_backend, diagnostics
