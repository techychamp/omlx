# Architecture Audit for Execution IR

## Existing Execution Sequencing
- Execution ordering is currently hardcoded in components like the `BatchGenerator` and specific `ExecutionBackend` implementations (e.g., `autoregressive_backend.py`, `experimental_diffusion_backend.py`).
- Pre-fill and decode sequences are managed by `scheduler.py` via `mlx-lm` APIs.
- Specifically, the `ExecutionEngine` triggers `generate_stream`, taking over execution sequencing dynamically.

## Scheduler Flow
- Requests enter a waiting queue.
- Moved to running state via continuous batching in `scheduler.py`.
- No intermediate representation determines the actual scheduling logic; it is inferred directly from the backend mode.

## Duplicated Execution Ordering
- Execution flows are split by backend rather than a unified logical layer. The `autoregressive_backend` and `experimental_diffusion_backend` have completely independent execution structures.
- Speculative execution relies on independent logic paths, duplicating basic forward/sample step representations.

## Proposal for IR
We will introduce `omlx.planner.ir` to sit right after `omlx.planner`. The `ExecutionPlanner` returns an `ExecutionPlan`. A new `IRBuilder` owned directly by the `Runtime` constructs the `ExecutionIR` from the plan. This isolates scheduling and execution from planning entirely.
