# SPDX-License-Identifier: Apache-2.0
"""
Execution Intermediate Representation (Execution IR).
"""

from .nodes import IRNode, IRNodeType
from .graph import ExecutionIR
from .builder import IRBuilder
from .validation import validate_ir, IRValidationError
from .passes import IROptimizationPass, IRPassRegistry

__all__ = [
    "IRNode",
    "IRNodeType",
    "ExecutionIR",
    "IRBuilder",
    "validate_ir",
    "IRValidationError",
    "IROptimizationPass",
    "IRPassRegistry",
]
