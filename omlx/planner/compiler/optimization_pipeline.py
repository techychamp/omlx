# SPDX-License-Identifier: Apache-2.0
"""
Optimization Pipeline orchestrating logical and physical passes.
"""

from .passes import LogicalPassRegistry, PhysicalPassRegistry
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR
import time

class OptimizationPipeline:
    """Applies a series of optimization passes sequentially."""
    def __init__(self, logical_registry: LogicalPassRegistry, physical_registry: PhysicalPassRegistry):
        self.logical_registry = logical_registry
        self.physical_registry = physical_registry

    def optimize_logical(self, ir: ExecutionIR) -> ExecutionIR:
        """Apply all registered logical optimization passes."""
        optimized_ir = ir
        for opt_pass in self.logical_registry.get_passes():
            optimized_ir = opt_pass.apply(optimized_ir)
        return optimized_ir

    def optimize_physical(self, ir: PhysicalIR) -> PhysicalIR:
        """Apply all registered physical optimization passes."""
        optimized_ir = ir
        for opt_pass in self.physical_registry.get_passes():
            optimized_ir = opt_pass.apply(optimized_ir)
        return optimized_ir
