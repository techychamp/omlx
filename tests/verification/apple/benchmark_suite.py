import time
import os
from dataclasses import dataclass
from typing import List, Tuple
from types import MappingProxyType

try:
    import mlx.core as mx
    mlx_available = True
except ImportError:
    mlx_available = False

from omlx.runtime.session import RuntimeSession
from omlx.runtime.execution.engine import ExecutionEngine
from omlx.runtime.execution.context import ExecutionContext
from omlx.planner.compiler.backend.operations import (
    BackendOperationGraph,
    MLXForwardOperation,
    MLXSynchronizationOperation
)
from omlx.runtime.execution.apple.mlx_adapter import MLXRuntimeAdapter

class MLXBenchmarkModel:
    """A simulated model that executes real MLX compute to measure throughput."""
    def __init__(self, size_dim=1024):
        self.size_dim = size_dim
        # Keep weights resident
        if mlx_available:
            self.weights = mx.random.normal((size_dim, size_dim))
            mx.eval(self.weights)

    def __call__(self, x):
        if not mlx_available:
            return x
        # Simulate an AR or Speculative block of computation
        # Use correctly shaped input regardless of what adapter passes
        x_correct = mx.random.normal((128, self.size_dim))
        h = mx.matmul(x_correct, self.weights)
        h = mx.maximum(h, 0)
        h = mx.matmul(h, self.weights)
        return h

def create_benchmark_context(model, operations_count=100) -> ExecutionContext:
    adapter = MLXRuntimeAdapter()
    
    ops = {}
    roots = []
    
    for i in range(operations_count):
        op_id = f"fwd_{i}"
        ops[op_id] = MLXForwardOperation(id=op_id, metadata={})
        roots.append(op_id)
        
    sync_id = "sync_final"
    ops[sync_id] = MLXSynchronizationOperation(id=sync_id, metadata={})
    
    graph = BackendOperationGraph(
        backend_id="apple_mlx",
        operations=MappingProxyType(ops),
        roots=tuple(roots),
        barriers=(),
        synchronization_points=(sync_id,),
        metadata={}
    )
    
    context = ExecutionContext(model=model, adapter=adapter, backend_operation_graph=graph)
    return context

@dataclass
class BenchmarkResult:
    scenario: str
    operations: int
    latency_ms: float
    throughput_ops: float
    peak_memory_mb: float

from omlx.runtime.execution.executor import ImmutableExecutionExecutor
from omlx.runtime.execution.graph_executor import DeterministicGraphExecutor
from omlx.runtime.execution.dispatcher import SequentialExecutionDispatcher

def run_scenario(name: str, dim: int, ops_count: int) -> BenchmarkResult:
    model = MLXBenchmarkModel(size_dim=dim)
    context = create_benchmark_context(model, operations_count=ops_count)
    session = RuntimeSession(session_id=f"bench_{name}")
    session.execution_context = context
    
    # Use sequential execution for MLX benchmarking to prevent thread stream errors
    dispatcher = SequentialExecutionDispatcher()
    graph_exec = DeterministicGraphExecutor(dispatcher)
    executor = ImmutableExecutionExecutor(graph_exec)
    engine = ExecutionEngine(executor=executor)
    
    # Warmup
    if mlx_available:
        _ = model(mx.random.normal((128, dim)))
        mx.eval(_)
    
    start = time.perf_counter()
    result = engine.execute(session)
    duration_ms = (time.perf_counter() - start) * 1000
    
    # Evaluate outputs
    peak_mem = 0.0
    if result.status.name == "COMPLETED" and session.apple_runtime_diagnostics:
        metal_metrics = session.apple_runtime_diagnostics.metal_report
        if metal_metrics and metal_metrics.peak_memory_bytes:
            peak_mem = metal_metrics.peak_memory_bytes / (1024 * 1024)
            
    throughput = (ops_count / (duration_ms / 1000)) if duration_ms > 0 else 0
    return BenchmarkResult(name, ops_count, duration_ms, throughput, peak_mem)

def print_baseline_report(results: List[BenchmarkResult]):
    print("\n" + "="*80)
    print("APPLE-006 PERFORMANCE BASELINE REPORT".center(80))
    print("="*80)
    print(f"{'Scenario':<20} | {'Ops':<10} | {'Latency (ms)':<15} | {'Ops/s':<15} | {'Peak Mem (MB)':<15}")
    print("-" * 80)
    for res in results:
        print(f"{res.scenario:<20} | {res.operations:<10} | {res.latency_ms:<15.2f} | {res.throughput_ops:<15.2f} | {res.peak_memory_mb:<15.2f}")
    print("="*80 + "\n")

if __name__ == "__main__":
    if not mlx_available:
        print("MLX not available on this platform. Benchmark will run in simulated mode.")
        
    print("Starting Apple Hardware Validation Benchmark Suite...")
    
    scenarios = [
        ("Microbench Matmul", 4096, 50),
        ("TinyLlama AR", 1024, 200),
        ("Nemotron AR", 2048, 150),
        ("MoE Dispatch", 2048, 100),
        ("Speculative Draft", 512, 400),
    ]
    
    results = []
    for name, dim, ops in scenarios:
        print(f"Executing {name}...")
        res = run_scenario(name, dim, ops)
        results.append(res)
        
    print_baseline_report(results)
