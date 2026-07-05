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
from .policy import ExecutionPolicy, BackendSelectionPolicy, get_policy_strategy
from .evaluation import BackendEvaluationReport
from .compatibility import CompatibilityChecker, CompatibilityReport
from .negotiation import BackendNegotiator, NegotiationDiagnostics
from .fallback import FallbackPlan, FallbackNode
from .diagnostics import BackendSelectionDiagnostics

class BackendSelectionFramework:
    def __init__(self, registry: BackendDescriptorRegistry) -> None:
        self.registry = registry

    def select_backend(
        self,
        plan: ExecutionPlan,
        cap_desc: CapabilityDescriptor,
        policy: ExecutionPolicy,
        candidate_ids: List[str]
    ) -> Tuple[str, BackendSelectionDiagnostics]:
        timestamp = time.time()

        evaluations = {}
        compatibility_reports = {}
        negotiations = {}
        fallback_nodes = []

        selected_backend = ""
        best_score = -1.0

        strategy = get_policy_strategy(policy.selection_policy)

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

            # 3. Evaluation
            eval_report = BackendEvaluationReport(
                backend_id=backend_id,
                is_compatible=comp_report.is_compatible,
                estimated_latency_ms=backend_desc.estimated_latency,
                estimated_memory_mb=backend_desc.estimated_memory_usage,
                estimated_throughput_tps=backend_desc.estimated_throughput,
                estimated_startup_cost_ms=0.0,
                cache_compatibility_score=backend_desc.cache_efficiency,
                hardware_utilization_score=1.0,
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

        diagnostics = BackendSelectionDiagnostics(
            timestamp=timestamp,
            candidate_backends=tuple(candidate_ids),
            evaluations=MappingProxyType(evaluations),
            compatibility_reports=MappingProxyType(compatibility_reports),
            negotiations=MappingProxyType(negotiations),
            fallback_plan=fallback_plan,
            selected_backend=selected_backend
        )

        return selected_backend, diagnostics
