import time
from typing import Optional, Tuple
from omlx.planner.domains.bundle import PlanningBundle
from omlx.optimization.passes import OptimizationPass, PassCategory, CompilerStage, OptimizationContext
from .policy import AppleOptimizationPolicy, PlacementOptimization, AffinityOptimization, PlacementStrategy, UnifiedMemoryPolicy, ExecutionAffinityPreference
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
        
        memory_policy = None
        placement_strategy = None
        affinity_preference = ExecutionAffinityPreference.AUTO

        if self.policy.enable_unified_memory and device_plan.placement.strategy == "unified_memory":
            placements.append(PlacementOptimization(
                original_device=device_plan.placement.device_id,
                optimized_device="apple_silicon_unified",
                strategy="unified_memory_optimized",
                reason="Applied Apple Silicon unified memory optimization"
            ))
            
            memory_policy = UnifiedMemoryPolicy(
                preferred_execution_device="gpu",
                preferred_memory_residency="unified",
                allocation_priority=1,
                memory_reuse_hints=True,
                synchronization_hints="metal_events"
            )
            placement_strategy = PlacementStrategy(
                strategy_type="unified_memory",
                memory_policy=memory_policy
            )
            
            info.append("Applied Unified Memory optimization")
            info.append("Generated UnifiedMemoryPolicy and PlacementStrategy")
        else:
            # Fallback CPU memory policy
            memory_policy = UnifiedMemoryPolicy(
                preferred_execution_device="cpu",
                preferred_memory_residency="shared",
                allocation_priority=0,
                memory_reuse_hints=False,
                synchronization_hints="none"
            )
            placement_strategy = PlacementStrategy(
                strategy_type="discrete",
                memory_policy=memory_policy
            )
            info.append("Generated default discrete CPU MemoryPolicy and PlacementStrategy")

        if device_plan.affinity.affinity_group == "apple_silicon_group":
            affinities.append(AffinityOptimization(
                original_affinity=device_plan.affinity.affinity_group,
                optimized_affinity="apple_silicon_high_perf",
                priority_adjustment=10,
                reason="Elevated priority for Apple Silicon high performance group"
            ))
            affinity_preference = ExecutionAffinityPreference.GPU
            info.append("Applied Affinity priority adjustment")
            info.append("Set ExecutionAffinityPreference to GPU")
        elif device_plan.affinity.affinity_group == "cpu_only":
            affinity_preference = ExecutionAffinityPreference.CPU
            info.append("Set ExecutionAffinityPreference to CPU")
        elif device_plan.affinity.affinity_group == "mlx_preferred":
            affinity_preference = ExecutionAffinityPreference.MLX
            info.append("Set ExecutionAffinityPreference to MLX")

        latency_ms = (time.time() - start_time) * 1000

        report = AppleOptimizationReport(
            is_optimized=len(placements) > 0 or len(affinities) > 0 or memory_policy is not None,
            placements=placements,
            affinities=affinities,
            placement_strategy=placement_strategy,
            memory_policy=memory_policy,
            affinity_preference=affinity_preference,
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
