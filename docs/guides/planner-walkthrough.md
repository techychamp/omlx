# Execution Planner Walkthrough

The Execution Planner is responsible for translating a `CapabilityDescriptor` into an `ExecutionPlan`. It takes the resolved capabilities of a model (such as whether it supports speculative decoding, streaming, or what its attention type is) and makes high-level planning decisions about how that model should be executed.

## Key Concepts

- **No Execution**: The planner does *not* execute code, allocate tensors, or interact with MLX.
- **Immutability**: It produces an immutable `ExecutionPlan` dataclass.
- **Optimization Passes**: The plan can be modified via `PlanningPass` instances before it is finalized.

## Example Flow

1. A request comes in, and the `CapabilityResolver` produces a `CapabilityDescriptor`.
2. The `RuntimeBuilder` creates a `Runtime` containing an `ExecutionPlanner`.
3. `execution_planner.plan(descriptor)` is called.
4. The base plan is created (backend selected, execution mode determined).
5. Registered optimization passes modify the mutable plan dictionary.
6. The plan is converted into a frozen `ExecutionPlan` dataclass.
7. Validation checks are run (`validate_plan`).
8. The final plan is returned to be used by the rest of the runtime.
