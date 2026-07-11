# Future Extension Guide

The completion of BACKEND-005 leaves the architecture in a clean state, ready for advanced compiler and runtime features.

## Upcoming Milestones & Recommendations

### 1. Asynchronous Execution
The current `SequentialExecutionDispatcher` blocks on each `adapter.execute()` call. For future milestones:
- Implement an `AsyncExecutionDispatcher` that leverages `asyncio` to dispatch non-dependent operations concurrently.
- The `MLXAdapter` is already stateless and thread-safe, so it can be called safely from multiple threads or async workers.

### 2. Streaming Decode
To replace Phase B (`mlx_lm.generate`) with a purely compiler-driven approach:
- Implement a generation loop in the Runtime (e.g., inside `TransformerExecutionEngine`).
- The runtime should iteratively feed the `BackendOperationGraph` back into the `ExecutionDispatcher`, appending new tokens to the `ExecutionContext` between steps.
- This will require the implementation of a native OMLX sampler in the runtime.

### 3. Apple Silicon Unified Memory Optimizations
Because the `MLXAdapter` uses `mx.eval()` cleanly on synchronization operations, memory optimization passes can be added to the compiler.
- Insert `MLXSynchronizationOperation` boundaries precisely where tensors must be materialized (e.g., prior to a sampler).
- Keep intermediate computations (e.g., multi-layer outputs) implicit to take advantage of MLX's lazy evaluation and unified memory layout.

### 4. Speculative Execution & Predictive Scheduling
- The `ExecutionContext` can be extended to carry multiple candidate token sequences.
- The `GraphScheduler` can emit branching logic.
- The `MLXAdapter` will handle batch-level `MLXForwardOperation` dispatches, completely abstracted away from the speculative logic.
