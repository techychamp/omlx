from omlx.planner.domains.bundle import PlanningBundle
from omlx.optimization.apple.policy import AppleOptimizationPolicy
from omlx.optimization.apple.optimization import AppleDeviceOptimizationPass
from omlx.optimization.passes import OptimizationContext
from omlx.planner.device.artifacts import DevicePlan, ExecutionPlacement, ExecutionAffinity

def test_apple_device_optimization_with_plan():
    policy = AppleOptimizationPolicy()
    optimization_pass = AppleDeviceOptimizationPass(policy)

    device_plan = DevicePlan(
        placement=ExecutionPlacement(device_id="default", strategy="unified_memory"),
        affinity=ExecutionAffinity(affinity_group="apple_silicon_group", priority=50)
    )

    bundle = PlanningBundle(device_plan=device_plan)
    context = OptimizationContext()

    optimized_bundle = optimization_pass.apply(bundle, context)

    assert "apple_optimization_report" in optimized_bundle.metadata
    report = optimized_bundle.metadata["apple_optimization_report"]

    assert report.is_optimized
    assert len(report.placements) == 1
    assert report.placements[0].optimized_device == "apple_silicon_unified"
    assert len(report.affinities) == 1
    assert report.affinities[0].optimized_affinity == "apple_silicon_high_perf"

def test_apple_device_optimization_no_plan():
    policy = AppleOptimizationPolicy()
    optimization_pass = AppleDeviceOptimizationPass(policy)

    bundle = PlanningBundle()
    context = OptimizationContext()

    optimized_bundle = optimization_pass.apply(bundle, context)

    # Should not optimize if no device plan exists
    assert "apple_optimization_report" not in optimized_bundle.metadata
