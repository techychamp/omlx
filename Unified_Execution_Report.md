# Unified Execution Report
The canonical execution pipeline handles all graph types:
- ExecutionGraph
- CacheExecutionGraph
- MemoryExecutionGraph
- BatchExecutionGraph
- SpeculativeExecutionGraph
- ExpertExecutionGraph
- DiffusionExecutionGraph
by executing them sequentially or concurrently through the single Executor instance, driven by the deterministic progression of phases: Preparation, Resource Initialization, Execution, Synchronization, Completion, and Cleanup.
# User Review Required
