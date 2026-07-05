# SCHED-001 Documentation

## Scheduler Architecture
The GraphScheduler analyzes `BackendOperationGraph` instances without executing any backend operations. It produces an immutable `ExecutionSchedule` containing ordered operations, dependency levels, and execution groups. It delegates analysis to `DependencyAnalyzer` and `CriticalPathAnalyzer`.

## Execution Schedule Guide
The `ExecutionSchedule` is the central immutable artifact produced by the scheduler. It contains the deterministic execution order required by the dispatcher, as well as extensive statistics and diagnostics.

## Execution Group Guide
An `ExecutionGroup` represents a set of operations that share the same dependency level. Operations within a group where `parallelizable=True` can theoretically be dispatched concurrently by an asynchronous engine.

## Dependency Analysis Guide
`DependencyAnalyzer` performs topological sorting to detect cycles, identify roots and leaves, and compute fan-in/fan-out metrics. It produces a `DependencyAnalysisResult`.

## Critical Path Guide
`CriticalPathAnalyzer` calculates the longest dependency chain in the graph to estimate minimum execution latency structurally, completely avoiding runtime timing.

## Scheduling Policies Guide
- `SEQUENTIAL`: Basic topological traversal.
- `DEPENDENCY_DRIVEN`: Groups operations strictly by their dependency depth.
(Other policies act as placeholders for future optimization strategies without altering correct execution semantics).

## Migration Report
The `DeterministicGraphExecutor` was updated to instantiate and invoke the `GraphScheduler`. The scheduler now determines the `execution_order` which is passed to the `ExecutionDispatcher`. Existing execution logic and semantics remain untouched. No changes were made to `BackendAdapter` or `RuntimeCompilerService`.

## Rollback Guide
To rollback, revert the changes in `omlx/runtime/execution/graph_executor.py` to restore the inline topological sort algorithm, and remove the `omlx/runtime/scheduling/` directory.

## Recommendations for EXEC-002
With the `GraphScheduler` producing `ExecutionGroup`s with `parallelizable` flags, the next step (EXEC-002) can safely implement asynchronous parallel execution within the `ExecutionEngine` and `ExecutionDispatcher` without needing to perform dependency analysis at runtime.
