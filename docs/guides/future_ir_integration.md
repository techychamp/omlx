# Future IR Integration Notes

The `ExecutionPlan` is designed to be the canonical input for the future **Execution IR** layer.

Currently, the planner produces high-level hints (e.g., `execution_backend = 'autoregressive'`). In upcoming phases (e.g., IMP-008), the system will introduce a Lowering phase. The lowering phase will take the `ExecutionPlan` and compile it into a `Logical IR` (a directed acyclic graph of nodes like `Forward`, `Sample`), which will then be lowered into `Physical IR` (Metal kernels).

Because `ExecutionPlan` is frozen, the compiler can safely rely on its attributes as invariant source truths during the lowering phase.
