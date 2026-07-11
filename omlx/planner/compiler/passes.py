# SPDX-License-Identifier: Apache-2.0
"""
Compiler passes for Logical and Physical IR.
"""
from __future__ import annotations
import abc
from typing import List, TypeVar, Generic
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR

T = TypeVar("T")

class CompilerPass(abc.ABC, Generic[T]):
    """Abstract base class for a compiler pass over a specific IR type."""
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def apply(self, ir: T) -> T:
        pass

class LogicalPass(CompilerPass[ExecutionIR]):
    """Pass operating on Logical Execution IR."""
    pass

class PhysicalPass(CompilerPass[PhysicalIR]):
    """Pass operating on Physical Execution IR."""
    pass

class CompilerPassRegistry(Generic[T]):
    """Registry for compiler passes."""
    def __init__(self):
        self._passes: List[CompilerPass[T]] = []

    def register(self, opt_pass: CompilerPass[T]) -> None:
        self._passes.append(opt_pass)

    def get_passes(self) -> List[CompilerPass[T]]:
        return list(self._passes)

class LogicalPassRegistry(CompilerPassRegistry[ExecutionIR]):
    pass

class PhysicalPassRegistry(CompilerPassRegistry[PhysicalIR]):
    pass
