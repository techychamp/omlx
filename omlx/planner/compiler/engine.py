# SPDX-License-Identifier: Apache-2.0
"""
Compiler Engine that orchestrates the full pipeline.
"""
from __future__ import annotations
import logging
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR
from .passes import LogicalPassRegistry, PhysicalPassRegistry
from .lowering import LoweringEngine

logger = logging.getLogger("omlx.compiler")

class CompilerEngine:
    """Orchestrates the entire compilation pipeline."""
    def __init__(self,
                 logical_registry: LogicalPassRegistry | None = None,
                 physical_registry: PhysicalPassRegistry | None = None,
                 lowering_engine: LoweringEngine | None = None):
        self.logical_registry = logical_registry or LogicalPassRegistry()
        self.physical_registry = physical_registry or PhysicalPassRegistry()
        self.lowering_engine = lowering_engine or LoweringEngine()

    def compile(self, logical_ir: ExecutionIR) -> PhysicalIR:
        """Runs the full compiler pipeline: Logical Passes -> Lowering -> Physical Passes."""

        # 1. Logical Optimization
        optimized_logical_ir = logical_ir
        for opt_pass in self.logical_registry.get_passes():
            logger.debug(f"Applying logical pass: {opt_pass.name}")
            optimized_logical_ir = opt_pass.apply(optimized_logical_ir)

        # 2. Lowering
        logger.debug("Lowering Logical IR to Physical IR")
        physical_ir = self.lowering_engine.lower(optimized_logical_ir)

        # 3. Physical Optimization
        optimized_physical_ir = physical_ir
        for opt_pass in self.physical_registry.get_passes():
            logger.debug(f"Applying physical pass: {opt_pass.name}")
            optimized_physical_ir = opt_pass.apply(optimized_physical_ir)

        return optimized_physical_ir
