# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import abc
import time
from enum import Enum
from typing import Any, Generic, List, TypeVar, Optional, Dict, Set, Tuple
from dataclasses import dataclass, field

T = TypeVar("T")

class PassCategory(Enum):
    CANONICALIZATION = "canonicalization"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    SIMPLIFICATION = "simplification"
    NORMALIZATION = "normalization"
    DIAGNOSTICS = "diagnostics"
    VERIFICATION = "verification"
    BACKEND_PREPARATION = "backend_preparation"
    METADATA_OPTIMIZATION = "metadata_optimization"

@dataclass(frozen=True)
class DiagnosticReport:
    pass_name: str
    category: PassCategory
    status: str  # "Executed", "Skipped", "Failed"
    duration_ms: float
    messages: List[str] = field(default_factory=list)

@dataclass
class OptimizationStats:
    executed_passes: int = 0
    skipped_passes: int = 0
    failed_passes: int = 0
    total_duration_ms: float = 0.0
    execution_order: List[str] = field(default_factory=list)
    graph_reductions: int = 0
    metadata_reductions: int = 0
    dependency_reductions: int = 0
    diagnostics: List[DiagnosticReport] = field(default_factory=list)

class BasePass(abc.ABC, Generic[T]):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def category(self) -> PassCategory:
        pass

    @property
    def required_passes(self) -> Set[str]:
        return set()

    @property
    def optional_passes(self) -> Set[str]:
        return set()

    @property
    def conflicting_passes(self) -> Set[str]:
        return set()

    @property
    def supported_stages(self) -> Set[str]:
        return {"CapabilityDescriptor", "ExecutionPlan", "LogicalIR", "PhysicalIR", "BackendOperationGraph"}

class AnalysisPass(BasePass[T]):
    @abc.abstractmethod
    def analyze(self, artifact: T) -> Dict[str, Any]:
        pass

class OptimizationPass(BasePass[T]):
    @abc.abstractmethod
    def apply(self, artifact: T) -> T:
        pass

class ValidationPass(BasePass[T]):
    @abc.abstractmethod
    def validate(self, artifact: T) -> None:
        pass
