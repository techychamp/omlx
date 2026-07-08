import time
import sys
import types
from unittest.mock import MagicMock

# Simulate MLX for benchmark
class MockMX:
    @staticmethod
    def array(val): return val
    @staticmethod
    def eval(*args): 
        # fake small sleep to simulate kernel dispatch overhead
        time.sleep(0.001)

mock_mlx = types.ModuleType("mlx")
mock_mlx_core = types.ModuleType("mlx.core")
mock_mlx_core.array = MockMX.array
mock_mlx_core.eval = MockMX.eval

mock_metal = types.ModuleType("mlx.core.metal")
mock_metal.set_cache_limit = lambda x: None
mock_metal.get_peak_memory = lambda: 1024000
mock_metal.get_active_memory = lambda: 512000
mock_metal.get_cache_memory = lambda: 512000
mock_mlx_core.metal = mock_metal

sys.modules["mlx"] = mock_mlx
sys.modules["mlx.core"] = mock_mlx_core
sys.modules["mlx.core.metal"] = mock_metal

from omlx.planner.compiler.backend.operations import BackendOperationGraph, MLXForwardOperation, MLXSynchronizationOperation
from omlx.runtime.execution.context import ExecutionContext, AppleExecutionMetadata
from omlx.runtime.execution.apple.mlx_adapter import MLXRuntimeAdapter
from omlx.runtime.session import RuntimeSession
from omlx.runtime.execution.engine import ExecutionEngine
from omlx.runtime.execution.executor import ImmutableExecutionExecutor
from omlx.runtime.execution.graph_executor import DeterministicGraphExecutor
from omlx.runtime.execution.dispatcher import SequentialExecutionDispatcher
from types import MappingProxyType

class MockModel:
    def __call__(self, x):
        time.sleep(0.0001)  # tiny forward cost
        return "mock_logits"

def run_benchmark(batch_size: int):
    # Create operations
    ops = {}
    roots = []
    
    # We will issue N forwards and 1 synchronization
    for i in range(batch_size):
        op = MLXForwardOperation(id=f"fwd_{i}")
        ops[f"fwd_{i}"] = op
        roots.append(f"fwd_{i}")
        
    sync_op = MLXSynchronizationOperation(id="sync")
    ops["sync"] = sync_op
    roots.append("sync")
    
    graph = BackendOperationGraph(backend_id="mlx", operations=MappingProxyType(ops), roots=tuple(roots), barriers=(), synchronization_points=(), metadata={})
    
    adapter = MLXRuntimeAdapter()
    context = ExecutionContext(
        request_context=MagicMock(),
        backend_operation_graph=graph,
        adapter=adapter,
        model=MockModel(),
        apple_execution_metadata=AppleExecutionMetadata(
            device_plan=MagicMock(),
            placement=MagicMock(),
            optimization_report=MagicMock()
        )
    )
    
    session = RuntimeSession.create()
    session.execution_context = context
    
    dispatcher = SequentialExecutionDispatcher()
    executor = ImmutableExecutionExecutor(DeterministicGraphExecutor(dispatcher))
    engine = ExecutionEngine(executor)
    
    start = time.perf_counter()
    result = engine.execute(session)
    end = time.perf_counter()
    
    diag = session.apple_runtime_diagnostics
    
    print(f"Batch Size: {batch_size}")
    print(f"Total Time: {(end - start)*1000:.2f} ms")
    if diag and diag.batch_statistics:
        print(f"Operations Batched: {diag.batch_statistics.total_operations_batched}")
        print(f"Batches Executed: {diag.batch_statistics.total_batches_executed}")
    if diag and diag.metal_report:
        print(f"Peak Metal Memory: {diag.metal_report.peak_memory_bytes}")
    
    return (end - start) * 1000

print("Running Unbatched vs Batched Baseline...")
time_1 = sum(run_benchmark(1) for _ in range(10))
print(f"10 runs of batch_size 1: {time_1:.2f} ms")

print("\n---")
time_10 = run_benchmark(10)
print(f"1 run of batch_size 10: {time_10:.2f} ms")
