# Execution Lifecycle Guide

1. `CREATED`: Initial instantiation, optionally pulled from Queue.
2. `PLANNED`: Compilation phase completed successfully.
3. `READY`: Contexts applied and execution prepared.
4. `EXECUTING`: Handoff to `ExecutionEngine`.
5. `COMPLETED` / `FAILED`: Engine finalizes the state.