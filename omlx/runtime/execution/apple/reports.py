from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

@dataclass(frozen=True)
class AppleExecutionPerformanceReport:
    operation_id: str
    latency_ms: float
    status: str
    error_message: Optional[str] = None
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class UnifiedMemoryPerformanceReport:
    memory_policy_applied: str
    cache_limit_bytes: Optional[int] = None
    bytes_transferred: int = 0
    synchronization_events: int = 0
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class PlacementExecutionReport:
    placement_strategy_applied: str
    actual_device: str
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class MetalExecutionPerformanceReport:
    peak_memory_bytes: Optional[int] = None
    active_memory_bytes: Optional[int] = None
    cache_memory_bytes: Optional[int] = None
    utilization_percent: Optional[float] = None
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class ExecutionBatchStatistics:
    total_operations_batched: int = 0
    total_batches_executed: int = 0
    total_synchronization_events: int = 0
    average_batch_size: float = 0.0

@dataclass(frozen=True)
class AppleRuntimeStatistics:
    total_execution_latency_ms: float = 0.0
    total_memory_transfers: int = 0
    total_placement_validations: int = 0

@dataclass(frozen=True)
class AppleRuntimeDiagnostics:
    execution_reports: Tuple[AppleExecutionPerformanceReport, ...] = field(default_factory=tuple)
    memory_report: Optional[UnifiedMemoryPerformanceReport] = None
    placement_report: Optional[PlacementExecutionReport] = None
    metal_report: Optional[MetalExecutionPerformanceReport] = None
    batch_statistics: Optional[ExecutionBatchStatistics] = None
    statistics: AppleRuntimeStatistics = field(default_factory=AppleRuntimeStatistics)
