# Execution Flow Diagram

The target architecture enforces strict separation of concerns, ensuring that the backend adapter handles only physical execution and not scheduling or state management.

```mermaid
graph TD
    A[Runtime] -->|Initiates Compilation| B(RuntimeCompilerService)
    B -->|Plans| C[ExecutionPlan]
    C -->|Constructs| D[LogicalIR]
    D -->|Lowers| E[PhysicalIR]
    E -->|Translates via MLXAdapter| F[BackendOperationGraph]
    F -->|Schedules via GraphScheduler| G[ExecutionSchedule]
    G -->|Coordinates| H(ExecutionEngine)
    H -->|Dispatches per op| I(ExecutionDispatcher)
    I -->|Executes single op| J(MLXAdapter.execute)

    J -.->|MLXForwardOperation| K[context.model forward]
    J -.->|MLXSynchronizationOperation| L[mx.eval barrier]
    J -.->|MLXSamplingOperation| M[Returns Unsupported]

    K --> N[ExecutionResult]
    L --> N
    M --> N

    N -->|Returns to Engine| H
```

### Flow Walkthrough

1. The `RuntimeCompilerService` takes a request and runs it through the capability resolver, planner, and IR builder to produce a `PhysicalIR`.
2. The `MLXAdapter` performs static translation (ahead-of-time) of the `PhysicalIR` into a `BackendOperationGraph`.
3. The `GraphScheduler` sequences the operations from the graph into an `ExecutionSchedule`.
4. The `ExecutionEngine` iterates over the schedule. For each scheduled operation, it delegates to the `ExecutionDispatcher`.
5. The `ExecutionDispatcher` calls `MLXAdapter.execute(operation, context)`.
6. The `MLXAdapter` acts solely as a kernel dispatcher, using lightweight references from the `ExecutionContext` (such as the model instance) to execute the specific operation. It does not own the model lifecycle or generation loop.
