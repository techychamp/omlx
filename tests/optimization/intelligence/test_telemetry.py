# SPDX-License-Identifier: Apache-2.0
from omlx.optimization.intelligence.telemetry import OptimizationTelemetry
from omlx.optimization.intelligence.cost_models import CostEstimate, ExecutionCost
from omlx.optimization.intelligence.statistics import IntelligenceStatisticsTracker

def test_telemetry_creation():
    t = OptimizationTelemetry(
        pass_name="TestPass",
        applied=True,
        estimated_improvement=CostEstimate(execution=ExecutionCost(latency_ms=2.5))
    )
    assert t.pass_name == "TestPass"
    assert t.applied is True
    assert t.estimated_improvement.execution.latency_ms == 2.5

def test_statistics_tracker():
    tracker = IntelligenceStatisticsTracker()

    t1 = OptimizationTelemetry(pass_name="Pass1", applied=True, analysis_reused=True)
    t2 = OptimizationTelemetry(pass_name="Pass2", applied=False, reason_skipped="Not profitable")

    tracker.record_telemetry(t1)
    tracker.record_telemetry(t2)
    tracker.record_phase_timing("select", 15.0)

    snap = tracker.get_snapshot()
    assert snap["applied_passes"] == 1
    assert snap["skipped_passes"] == 1
    assert snap["analysis_reuses"] == 1
    assert snap["phase_timings_ms"]["select"] == 15.0
    assert snap["telemetry_count"] == 2
