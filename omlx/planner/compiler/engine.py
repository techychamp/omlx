# SPDX-License-Identifier: Apache-2.0
"""
Compiler Engine that orchestrates the full pipeline.
"""
from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from omlx.planner.compiler.cache.utils import compute_cache_key

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.analysis import GraphAnalyzer
from omlx.planner.ir.physical.graph import PhysicalIR
from .passes import LogicalPassRegistry, PhysicalPassRegistry
from .lowering import LoweringEngine
from .cache.manager import CompilerCacheManager
from .optimization_pipeline import OptimizationPipeline
from .dependency_tracker import DependencyTracker
from .backend.adapter import BaseBackendAdapter
from .backend.registry import AdapterRegistry
from omlx.runtime.observability import get_observer
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.compiler.transformation.pass_ import FusionRealizationPass
from omlx.optimization.fusion import FusionEvaluator
from omlx.planner.domains.moe.transformation.pass_ import MoERealizationPass
from omlx.planner.domains.diffusion.transformation.pass_ import DiffusionRealizationPass
from omlx.planner.domains.memory.transformation.pass_ import MemoryRealizationPass
from omlx.planner.compiler.batch.transformation.pass_ import BatchRealizationPass
from omlx.planner.domains.cache.transformation.pass_ import CacheRealizationPass



logger = logging.getLogger("omlx.compiler")

class CompilerEngine:
    """Orchestrates the entire compilation pipeline with incremental compilation."""
    def __init__(self,
                 logical_registry: LogicalPassRegistry | None = None,
                 physical_registry: PhysicalPassRegistry | None = None,
                 lowering_engine: LoweringEngine | None = None,
                 cache_manager: CompilerCacheManager | None = None,
                 dependency_tracker: DependencyTracker | None = None):
        self.logical_registry = logical_registry or LogicalPassRegistry()
        self.physical_registry = physical_registry or PhysicalPassRegistry()
        self.cache_manager = cache_manager
        self.dependency_tracker = dependency_tracker or DependencyTracker()
        self.lowering_engine = lowering_engine or LoweringEngine(cache_manager=cache_manager, dependency_tracker=self.dependency_tracker)
        self.optimization_pipeline = OptimizationPipeline(self.logical_registry, self.physical_registry)

    def compile(self, logical_ir: ExecutionIR, planning_bundle: Optional[PlanningBundle] = None) -> PhysicalIR:
        """Runs the full compiler pipeline: Planning -> IR -> Logical Passes -> Lowering -> Physical Passes."""
        with get_observer().observe_phase("Compilation", "Compiler", "compile"):

            # Conditionally inject Cache realization pass if plan is provided

            if planning_bundle and planning_bundle.cache_plan:

                 cache_pass = CacheRealizationPass(planning_bundle.cache_plan)

                 logical_ir = cache_pass.apply(logical_ir)

                 if cache_pass.report:

                     get_observer().track_artifact("CacheTransformationReport", cache_pass.report)


            # Conditionally inject fusion realization pass if plan is provided
            if planning_bundle and planning_bundle.fusion_plan:
                 evaluator = FusionEvaluator()
                 decision = evaluator.evaluate_plan(planning_bundle.fusion_plan, None, None)
                 get_observer().track_artifact("FusionOptimizationDecision", decision)

                 if decision.accepted:
                     fusion_pass = FusionRealizationPass(planning_bundle.fusion_plan)
                     logical_ir = fusion_pass.apply(logical_ir)
                     get_observer().track_artifact("FusionTransformationReport", fusion_pass.descriptor)

            # Conditionally inject MoE realization pass if plan is provided
            if planning_bundle and planning_bundle.moe_plan:
                 moe_pass = MoERealizationPass(planning_bundle.moe_plan)
                 logical_ir = moe_pass.apply(logical_ir)
                 if moe_pass.report:
                     get_observer().track_artifact("MoETransformationReport", moe_pass.report)

            # Conditionally inject Diffusion realization pass if plan is provided
            if planning_bundle and planning_bundle.diffusion_plan:
                 diffusion_pass = DiffusionRealizationPass(planning_bundle.diffusion_plan)
                 logical_ir = diffusion_pass.apply(logical_ir)
                 if diffusion_pass.report:
                     get_observer().track_artifact("DiffusionTransformationReport", diffusion_pass.report)

            # Conditionally inject Memory realization pass if plan is provided
            if planning_bundle and planning_bundle.memory_plan:
                 memory_pass = MemoryRealizationPass(planning_bundle.memory_plan)
                 logical_ir = memory_pass.apply(logical_ir)
                 if memory_pass.report:
                     get_observer().track_artifact("MemoryRealizationReport", memory_pass.report)
            # Conditionally inject Speculation realization pass if plan is provided
            if planning_bundle and getattr(planning_bundle, 'speculation_plan', None):
                 from omlx.planner.domains.speculation.transformation.pass_ import SpeculationRealizationPass
                 spec_pass = SpeculationRealizationPass(planning_bundle.speculation_plan)
                 logical_ir = spec_pass.apply(logical_ir)
                 if spec_pass.report:
                     planning_bundle.speculative_graph = spec_pass.report.speculative_graph
                     get_observer().track_artifact("SpeculativeRealizationReport", spec_pass.report)
            # Conditionally inject Batch realization pass if plan is provided
            if planning_bundle and getattr(planning_bundle, 'batch_plan', None):
                 batch_pass = BatchRealizationPass(planning_bundle.batch_plan)
                 logical_ir = batch_pass.apply(logical_ir)
                 if batch_pass.report:
                     get_observer().track_artifact("BatchTransformationReport", batch_pass.report)

            # 1. Logical Optimization
            logger.debug("Applying logical passes")
            optimized_logical_ir = self.optimization_pipeline.optimize_logical(logical_ir)
            get_observer().track_artifact("LogicalIR", optimized_logical_ir)

            # Run Graph Analysis
            analyzer = GraphAnalyzer()
            report = analyzer.analyze(optimized_logical_ir)
            get_observer().track_artifact("LogicalIR_Analysis", report)
            get_observer().record_graph_metrics(report.statistics)

            if not report.validation.is_valid:
                for diag in report.validation.diagnostics:
                    get_observer().add_diagnostic(f"Graph Analysis: {diag.message}")

            # 2. Lowering
            logger.debug("Lowering Logical IR to Physical IR")
            physical_ir = self.lowering_engine.lower(optimized_logical_ir)

            # 3. Physical Optimization
            logger.debug("Applying physical passes")
            optimized_physical_ir = self.optimization_pipeline.optimize_physical(physical_ir)
            get_observer().track_artifact("PhysicalIR", optimized_physical_ir)

            return optimized_physical_ir

    def translate(self, physical_ir: PhysicalIR, adapter: BaseBackendAdapter) -> Any:
        """Translates the Physical IR into a Backend Operation Graph using the adapter."""
        logger.debug(f"Translating Physical IR using adapter {adapter.__class__.__name__}")

        with get_observer().observe_phase("Compilation", "Compiler", "translate"):
            adapter.cache_manager = self.cache_manager
            adapter.dependency_tracker = self.dependency_tracker
            result = adapter.translate_with_cache(physical_ir)
            get_observer().track_artifact("BackendOperationGraph", result)

            return result
