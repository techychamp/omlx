# SPDX-License-Identifier: Apache-2.0
"""
Compiler Engine that orchestrates the full pipeline.
"""
from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from omlx.planner.compiler.cache.utils import compute_cache_key

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR
from .passes import LogicalPassRegistry, PhysicalPassRegistry
from .lowering import LoweringEngine
from .cache.manager import CompilerCacheManager
from .optimization_pipeline import OptimizationPipeline
from .dependency_tracker import DependencyTracker
from .backend.adapter import BaseBackendAdapter
from .backend.registry import AdapterRegistry
from omlx.runtime.observability import get_observer

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

    def compile(self, logical_ir: ExecutionIR) -> PhysicalIR:
        """Runs the full compiler pipeline: Planning -> IR -> Logical Passes -> Lowering -> Physical Passes."""
        with get_observer().observe_phase("Compilation", "Compiler", "compile"):
            # 1. Logical Optimization
            logger.debug("Applying logical passes")
            optimized_logical_ir = self.optimization_pipeline.optimize_logical(logical_ir)
            get_observer().track_artifact("LogicalIR", optimized_logical_ir)

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
