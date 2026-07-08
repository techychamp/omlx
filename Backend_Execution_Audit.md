# Backend Execution Audit

## 1. Execution Flow Analysis
- The MLXAdapter currently mocks the `execute()` method, returning `{"status": "executed", "operation_id": operation.id, "backend": "mlx"}`.
- Dispatcher (`SequentialExecutionDispatcher`) loops through the execution order and calls `adapter.execute(op, context)`.
- `ExecutionContext` has placeholders for `model` and `tokenizer`, which are injected in the execution harness (Phase B in `RUN-001`).

## 2. Kernel Mapping Report
The `omlx/planner/compiler/backend/adapter.py` translates `PhysicalOperationType` into MLX operations:
- `FORWARD` -> `MLXForwardOperation`
- `SAMPLING` -> `MLXSamplingOperation`
- `CACHE_LOOKUP` -> `MLXCacheLookupOperation`
- `CACHE_UPDATE` -> `MLXCacheUpdateOperation`
- `SYNCHRONIZATION` -> `MLXSynchronizationOperation`
- `*` -> `MLXNoOpOperation`

### Real MLX Kernel Dispatch Plan:
1. `MLXForwardOperation`:
   - Inputs: typically input IDs and KV cache.
   - Output: Logits for the next token.
   - Action: `logits = context.model(input_ids)` (or similar depending on model implementation). If `mx.eval` is needed, it might be deferred or executed here.
2. `MLXSamplingOperation`:
   - As per architectural rules, sampling is NOT a backend responsibility. The backend should raise an `UnsupportedOperationError` or log a warning and return no-op for it, or it should be handled in the runtime (legacy/mocked for now, as it's not the backend's job).
3. `MLXCacheLookupOperation` & `MLXCacheUpdateOperation`:
   - MLX usually handles KV cache implicitly or through cache objects passed to the model. We may mock or do basic cache state updates in the backend if explicitly required, but `mlx_lm` models manage cache via `generate_step` or explicit `cache` objects. We'll instantiate/update cache objects as needed in the context.
4. `MLXSynchronizationOperation`:
   - `mx.eval()` might be called here to evaluate the computation graph, ensuring that all pending operations are executed on the GPU.

## 3. Operation Coverage Report
- **Supported Operations**: Forward, Synchronization.
- **Unsupported (by design in backend)**: Sampling (belongs to runtime).
- **Placeholder**: Cache Lookup/Update (needs alignment with how MLX models handle state).

## 4. Proposed Changes
- Update `MLXAdapter.execute(self, operation: BackendOperation, context: ExecutionContext) -> Any` to branch on `type(operation)`.
- Use `mx.eval` where appropriate (e.g., Synchronization).
- Catch `NotImplementedError` or unsupported operations and return appropriate diagnostics.
- Provide thread-safe execution (no global variables, using `context` for state).
- Create tests for these real implementations.
- Ensure `run_001_execution.py` still succeeds (it currently doesn't provide the real model to the compiler pipeline Phase A because it loads it in Phase B. We'll need to bridge Phase A and Phase B by injecting the loaded model into `ExecutionContext.model` as recommended in RUN-001).
