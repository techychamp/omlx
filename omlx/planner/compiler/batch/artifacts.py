from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class BatchSynchronizationGraph:
    batch_id: str
    nodes: List[Any] = field(default_factory=list)
    edges: List[Any] = field(default_factory=list)

@dataclass(frozen=True)
class BatchGroupingGraph:
    batch_id: str
    nodes: List[Any] = field(default_factory=list)
    edges: List[Any] = field(default_factory=list)

@dataclass(frozen=True)
class BatchExecutionGraph:
    batch_id: str
    grouping_graph: Optional[BatchGroupingGraph] = None
    synchronization_graph: Optional[BatchSynchronizationGraph] = None
    nodes: List[Any] = field(default_factory=list)
    edges: List[Any] = field(default_factory=list)

@dataclass(frozen=True)
class BatchExecutionDescriptor:
    batch_execution_graph: BatchExecutionGraph

@dataclass(frozen=True)
class BatchRealizationDiagnostic:
    code: str
    message: str

@dataclass(frozen=True)
class BatchRealizationStatistics:
    realization_latency_ms: float = 0.0
    batch_size: int = 0
    synchronization_count: int = 0
    dependency_count: int = 0

@dataclass(frozen=True)
class BatchRealizationReport:
    success: bool
    batch_execution_graph: Optional[BatchExecutionGraph] = None
    diagnostics: List[BatchRealizationDiagnostic] = field(default_factory=list)
    statistics: Optional[BatchRealizationStatistics] = None
