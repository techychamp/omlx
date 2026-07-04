# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Passes
"""

from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional, TypeVar

class PassCategory(Enum):
    CANONICALIZATION = auto()
    SIMPLIFICATION = auto()
    VALIDATION = auto()
    ANALYSIS = auto()
    OPTIMIZATION = auto()
    VERIFICATION = auto()
    BACKEND_PREPARATION = auto()
    DIAGNOSTICS = auto()

class CompilerStage(Enum):
    CAPABILITY_DESCRIPTOR = auto()
    EXECUTION_PLAN = auto()
    LOGICAL_IR = auto()
    PHYSICAL_IR = auto()
    BACKEND_OPERATION_GRAPH = auto()

T = TypeVar("T")

class OptimizationContext:
    """Holds state, statistics, and diagnostics for a pass execution."""
    def __init__(self, tracker: Any = None, stats: Any = None):
        self.tracker = tracker
        self.stats = stats

class BasePass(ABC):
    """Abstract base class for all compiler passes."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the pass."""
        pass

    @property
    @abstractmethod
    def category(self) -> PassCategory:
        """The category of the pass."""
        pass

    @property
    @abstractmethod
    def supported_stages(self) -> Tuple[CompilerStage, ...]:
        """Stages where this pass can be applied."""
        pass

    @property
    def required_passes(self) -> Tuple[str, ...]:
        """Names of passes that must run before this pass."""
        return ()

    @property
    def conflicting_passes(self) -> Tuple[str, ...]:
        """Names of passes that cannot be run with this pass."""
        return ()

    @property
    def optional_passes(self) -> Tuple[str, ...]:
        """Names of passes that, if present, should run before this pass."""
        return ()

    @abstractmethod
    def apply(self, artifact: T, context: OptimizationContext) -> T:
        """Applies the pass to the given artifact."""
        pass

class OptimizationPass(BasePass):
    """A pass that optimizes or mutates the artifact."""
    pass

class AnalysisPass(BasePass):
    """A pass that analyzes the artifact without mutating it."""

    def apply(self, artifact: T, context: OptimizationContext) -> T:
        """Applies analysis. Returns the artifact unmodified."""
        self.analyze(artifact, context)
        return artifact

    @abstractmethod
    def analyze(self, artifact: T, context: OptimizationContext) -> None:
        """Performs analysis on the given artifact."""
        pass
