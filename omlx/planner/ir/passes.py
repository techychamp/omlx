# SPDX-License-Identifier: Apache-2.0
"""
IR Optimization Passes.
"""

import abc
from typing import List
from .graph import ExecutionIR

class IROptimizationPass(abc.ABC):
    """Abstract base class for IR optimization passes."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the optimization pass."""
        pass

    @abc.abstractmethod
    def apply(self, ir: ExecutionIR) -> ExecutionIR:
        """Applies the optimization pass, returning a new, modified ExecutionIR."""
        pass

class IRPassRegistry:
    """Registry for IR optimization passes."""
    def __init__(self):
        self._passes: List[IROptimizationPass] = []

    def register(self, opt_pass: IROptimizationPass) -> None:
        """Registers a pass."""
        self._passes.append(opt_pass)

    def get_passes(self) -> List[IROptimizationPass]:
        """Returns all registered passes in order."""
        return list(self._passes)
