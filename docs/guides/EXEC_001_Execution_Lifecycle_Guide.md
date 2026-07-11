# Execution Lifecycle Guide

## Lifecycle Phases

1. **Pipeline Invocation**: The intent is passed to the `RuntimeCompilerService` to produce a `TranslationResult`.
2. **Context Creation**: The runtime builds an `ExecutionContext` with the `BackendOperationGraph`.
3. **Execution Delivery**: The context is passed to `ExecutionEngine.execute()`.
4. **Validation and Traversal**: The `GraphExecutor` iterates over the nodes.
5. **Dispatch**: The `ExecutionDispatcher` invokes backend adapters.
6. **Result Collection**: `ExecutionStatistics` are gathered and wrapped in an `ExecutionResult`.
