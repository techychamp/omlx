# SPDX-License-Identifier: Apache-2.0
"""
Execution Intermediate Representation (Execution IR).
"""

from .nodes import IRNode, IRNodeType
from .graph import ExecutionIR
from .builder import IRBuilder
from .validation import validate_ir, IRValidationError
from .passes import IROptimizationPass, IRPassRegistry

# Forward imports for easier access to the new subpackages
from .values.types import Value, ValueType
from .physical.graph import PhysicalIR
from .physical.operations import PhysicalOperation, PhysicalOperationType

__all__ = [
    "IRNode",
    "IRNodeType",
    "ExecutionIR",
    "IRBuilder",
    "validate_ir",
    "IRValidationError",
    "IROptimizationPass",
    "IRPassRegistry",
    "Value",
    "ValueType",
    "PhysicalIR",
    "PhysicalOperation",
    "PhysicalOperationType",
]
