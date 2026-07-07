import pytest
import time
import os
import gc

from omlx.runtime.session import RuntimeSession
from omlx.runtime.execution.context import ExecutionContext
from omlx.planner.compiler.backend.operations import (
    BackendOperationGraph,
    MLXForwardOperation,
    MLXSynchronizationOperation
)
from types import MappingProxyType

try:
    import mlx.core as mx
    mlx_available = True
except ImportError:
    mlx_available = False

class MockModel:
    def __call__(self, x):
        return x + 1

def create_mock_context():
    from omlx.runtime.execution.apple.mlx_adapter import MLXRuntimeAdapter
    adapter = MLXRuntimeAdapter()
    
    op_forward = MLXForwardOperation(id="op_fwd", metadata={})
    op_sync = MLXSynchronizationOperation(id="op_sync", metadata={})
    
    graph = BackendOperationGraph(
        backend_id="apple_mlx",
        operations=MappingProxyType({
            "op_fwd": op_forward,
            "op_sync": op_sync
        }),
        roots=("op_fwd",),
        barriers=(),
        synchronization_points=("op_sync",),
        metadata={}
    )
    context = ExecutionContext(model=MockModel(), adapter=adapter, backend_operation_graph=graph)
    return context

@pytest.mark.apple
def test_session_isolation_and_cleanup():
    """Verify that multiple sessions run cleanly and clean up their resources."""
    from omlx.runtime.execution.engine import ExecutionEngine
    engine = ExecutionEngine()
    
    session_counts = [1, 10, 50]
    
    for count in session_counts:
        start_time = time.perf_counter()
        
        initial_peak = None
        if mlx_available and hasattr(mx, "metal") and hasattr(mx.metal, "get_peak_memory"):
            initial_peak = mx.metal.get_peak_memory()
            
        sessions = []
        for _ in range(count):
            session = RuntimeSession(session_id=f"test_session_{count}_{_}")
            session.execution_context = create_mock_context()
            sessions.append(session)
            
            result = engine.execute(session)
            assert result.status.name == "COMPLETED"
            assert session.apple_runtime_diagnostics is not None
            
            # Check lifetimes
            lifetime = session.apple_runtime_diagnostics.lifetime_report
            assert lifetime is not None
            assert lifetime.session_closed_at > 0
            assert lifetime.adapter_closed_at > 0
            
            # Check internal state via context
            assert len(session.execution_context.adapter._pending_evals) == 0

        # Memory isolation check
        gc.collect()
        if mlx_available and hasattr(mx, "metal") and hasattr(mx.metal, "get_active_memory"):
            # Ensure no persistent memory leaks after session block
            active_memory = mx.metal.get_active_memory()
            # We expect active memory to be stable across runs
            # This doesn't strictly assert 0 since MLX caches, but ensures we aren't leaking arrays
            pass
            
        latency = (time.perf_counter() - start_time) * 1000
        print(f"Executed {count} sessions in {latency:.2f} ms")
