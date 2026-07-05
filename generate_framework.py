import os

os.makedirs("omlx/compiler/framework", exist_ok=True)
os.makedirs("omlx/compiler/passes", exist_ok=True)

with open("omlx/compiler/framework/__init__.py", "w") as f:
    f.write("# SPDX-License-Identifier: Apache-2.0\n")

with open("omlx/compiler/framework/passes.py", "w") as f:
    f.write("""# SPDX-License-Identifier: Apache-2.0
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
""")

with open("omlx/compiler/framework/manager.py", "w") as f:
    f.write("""# SPDX-License-Identifier: Apache-2.0
import time
from typing import Any, Generic, List, TypeVar, Optional, Dict, Set, Tuple
from collections import defaultdict, deque
from .passes import BasePass, AnalysisPass, OptimizationPass, ValidationPass, OptimizationStats, DiagnosticReport, PassCategory

T = TypeVar("T")

class PassDependencyError(Exception):
    pass

class PassManager(Generic[T]):
    def __init__(self, stage: str):
        self.stage = stage
        self._passes: Dict[str, BasePass[T]] = {}
        self.stats = OptimizationStats()

    def register(self, p: BasePass[T]) -> None:
        if p.name in self._passes:
            raise ValueError(f"Pass {p.name} is already registered.")
        if self.stage not in p.supported_stages:
            raise ValueError(f"Pass {p.name} does not support stage {self.stage}.")
        self._passes[p.name] = p

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        graph = defaultdict(set)

        # Validate conflicts
        for p_name, p in self._passes.items():
            for conflict in p.conflicting_passes:
                if conflict in self._passes:
                    raise PassDependencyError(f"Conflict: {p_name} conflicts with {conflict}")

        for p_name, p in self._passes.items():
            for req in p.required_passes:
                if req not in self._passes:
                    raise PassDependencyError(f"Missing required pass: {p_name} requires {req}")
                graph[p_name].add(req)
            for opt in p.optional_passes:
                if opt in self._passes:
                    graph[p_name].add(opt)

        return graph

    def schedule(self) -> List[BasePass[T]]:
        graph = self._build_dependency_graph()

        # Topological sort (Kahn's algorithm)
        in_degree = {name: 0 for name in self._passes}
        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1

        queue = deque([name for name in in_degree if in_degree[name] == 0])
        ordered = []

        while queue:
            node = queue.popleft()
            ordered.append(self._passes[node])
            for neighbor in [k for k, v in graph.items() if node in v]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Note: the graph built maps dependent -> dependency.
        # Kahn's usually goes dependency -> dependent.
        # Let's fix the graph direction for standard top-sort.
        # graph maps A -> B means A depends on B, so B must execute before A.
        # We need an edge B -> A.

        return self._correct_schedule()

    def _correct_schedule(self) -> List[BasePass[T]]:
        graph = self._build_dependency_graph()

        forward_graph = defaultdict(set)
        in_degree = {name: 0 for name in self._passes}

        for dependent, dependencies in graph.items():
            for dependency in dependencies:
                forward_graph[dependency].add(dependent)
                in_degree[dependent] += 1

        queue = deque([name for name in in_degree if in_degree[name] == 0])
        ordered = []

        while queue:
            node = queue.popleft()
            ordered.append(self._passes[node])
            for neighbor in forward_graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered) != len(self._passes):
            raise PassDependencyError("Circular dependency detected in pass schedule.")

        return ordered

    def execute(self, artifact: T) -> Tuple[T, Dict[str, Any]]:
        ordered_passes = self.schedule()
        current_artifact = artifact
        analysis_results = {}

        self.stats = OptimizationStats()
        start_pipeline = time.time()

        for p in ordered_passes:
            start_pass = time.time()
            messages = []
            status = "Executed"
            try:
                if isinstance(p, AnalysisPass):
                    res = p.analyze(current_artifact)
                    analysis_results[p.name] = res
                    messages.append(f"Analysis completed: {list(res.keys())}")
                elif isinstance(p, ValidationPass):
                    p.validate(current_artifact)
                    messages.append("Validation passed")
                elif isinstance(p, OptimizationPass):
                    current_artifact = p.apply(current_artifact)
                    messages.append("Optimization applied")

                duration = (time.time() - start_pass) * 1000
                self.stats.executed_passes += 1
                self.stats.execution_order.append(p.name)

            except Exception as e:
                duration = (time.time() - start_pass) * 1000
                self.stats.failed_passes += 1
                status = "Failed"
                messages.append(str(e))
                # Depending on strictness, we might re-raise or continue.
                # Assuming fail-fast for safety.
                raise
            finally:
                diag = DiagnosticReport(
                    pass_name=p.name,
                    category=p.category,
                    status=status,
                    duration_ms=duration,
                    messages=messages
                )
                self.stats.diagnostics.append(diag)

        self.stats.total_duration_ms = (time.time() - start_pipeline) * 1000
        return current_artifact, analysis_results
""")
