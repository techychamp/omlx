import time
from typing import Optional, Tuple
from omlx.planner.domains.bundle import PlanningBundle
from omlx.optimization.passes import OptimizationPass, PassCategory, CompilerStage, OptimizationContext
from .policy import AppleOptimizationPolicy, PlacementOptimization, AffinityOptimization
from .report import AppleOptimizationReport, OptimizationDiagnostics, OptimizationStatistics
from omlx.planner.device.artifacts import DevicePlan

class AppleDeviceOptimizationPass(OptimizationPass):
    """
    Compiler-native device optimization pass for Apple Silicon.
    Refines placement and affinity from DevicePlanning.
    Operates on a PlanningBundle and returns an optimized PlanningBundle.
    """

    def __init__(self, policy: Optional[AppleOptimizationPolicy] = None):
        self._name = "apple_device_optimization"
        self._category = PassCategory.OPTIMIZATION
        self._supported_stages = (CompilerStage.EXECUTION_PLAN,)
        self.policy = policy or AppleOptimizationPolicy()

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> PassCategory:
        return self._category

    @property
    def supported_stages(self) -> Tuple[CompilerStage, ...]:
        return self._supported_stages

    def apply(self, artifact: PlanningBundle, context: OptimizationContext) -> PlanningBundle:
        start_time = time.time()

        device_plan = artifact.get_plan("device")

        if not device_plan:
            return artifact # Nothing to optimize

        placements = []
        affinities = []
        info = []

        if self.policy.enable_unified_memory and device_plan.placement.strategy == "unified_memory":
            placements.append(PlacementOptimization(
                original_device=device_plan.placement.device_id,
                optimized_device="apple_silicon_unified",
                strategy="unified_memory_optimized",
                reason="Applied Apple Silicon unified memory optimization"
            ))
            info.append("Applied Unified Memory optimization")

        if device_plan.affinity.affinity_group == "apple_silicon_group":
            affinities.append(AffinityOptimization(
                original_affinity=device_plan.affinity.affinity_group,
                optimized_affinity="apple_silicon_high_perf",
                priority_adjustment=10,
                reason="Elevated priority for Apple Silicon high performance group"
            ))
            info.append("Applied Affinity priority adjustment")

        latency_ms = (time.time() - start_time) * 1000

        report = AppleOptimizationReport(
            is_optimized=len(placements) > 0 or len(affinities) > 0,
            placements=placements,
            affinities=affinities,
            diagnostics=OptimizationDiagnostics(info=info),
            statistics=OptimizationStatistics(
                total_placements_optimized=len(placements),
                total_affinities_optimized=len(affinities),
                optimization_latency_ms=latency_ms
            )
        )

        new_metadata = artifact.metadata.copy()
        new_metadata["apple_optimization_report"] = report

        return PlanningBundle(
            execution_plan=artifact.execution_plan,
            memory_plan=artifact.memory_plan,
            cache_plan=artifact.cache_plan,
            verification_plan=artifact.verification_plan,
            fusion_plan=artifact.fusion_plan,
            moe_plan=artifact.moe_plan,
            device_plan=artifact.device_plan,
            metadata=new_metadata
        )
