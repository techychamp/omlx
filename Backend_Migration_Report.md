# Backend Migration Report (BACKEND-005)

## Objective Met
Replaced the structural implementation of `MLXAdapter.execute()` with real MLX backend execution without bypassing the compiler runtime.

## Summary of Changes
- **`omlx/planner/compiler/backend/adapter.py`**:
  - Implemented `MLXAdapter.execute()` to explicitly handle specific `BackendOperation` subclasses.
  - Implemented `MLXForwardOperation` to extract `input_ids` from the runtime context and execute a real forward pass on `context.model`.
  - Implemented `MLXSynchronizationOperation` to call `mx.eval()`.
  - Enforced architectural boundaries by actively failing `MLXSamplingOperation`.
  - Added comprehensive structured diagnostics and performance timing for each operation execution.
- **`tests/run_001_execution.py`**:
  - Updated the harness to eagerly load the real model and tokenizer via `mlx_lm.utils.load`.
  - Injected the model and tokenizer into the `ExecutionContext` so that Phase A (the compiler pipeline) executes the `BackendOperationGraph` using real forward kernels.
  - Retained Phase B's compatibility shim to ensure functional parity and testing of legacy inference paths.
- **Tests**:
  - Created `tests/test_mlx_adapter_execute.py` to ensure each operation correctly succeeds or fails depending on its type and context state, and that the execution handles environments where `mlx` is not installed gracefully.

## Architectural Verification
- **ExecutionEngine ownership**: Remained unchanged. It iterates through the schedule.
- **BackendAdapter ownership**: The backend executes kernels but does NOT run decode loops, generate text, or sample tokens.
- **Sampling Separation**: Sampling explicitly fails in the backend, correctly confirming that it's a runtime-level concern.

## Regression Status
- `RUN-001` integration test continues to succeed, now performing actual (simulated or real, depending on system capability) MLX forward passes during Phase A rather than simple string mocks.
