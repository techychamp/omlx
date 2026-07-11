# Scheduler Decomposition Report

*Prepared for SCHED-003 extraction phase.*

## Current State
The monolithic `GraphScheduler` in `omlx/runtime/scheduling/scheduler.py` handles Graph parsing, heuristics, dependency traversal, queuing, and statistics generation in a tightly coupled loop across massive conditional `_build_from_X` functions.

## Suggested Future Modules (Decomposition Seams)

### 1. Graph Analysis Component
* **Boundary:** Parsing `BackendOperationGraph`, `ExecutionPhaseGraph`, or `ExpertExecutionGraph` to extract roots, leaves, graph depths, and critical paths.
* **Complexity:** Medium (Requires standardizing the traversal adapter interfaces).

### 2. Scheduling Policy Engine
* **Boundary:** Taking extracted topologies and evaluating them against `SchedulingPolicy` rules (e.g., `DEPENDENCY_DRIVEN` vs `SEQUENTIAL`) to generate an Execution Order mapping.
* **Complexity:** High (Determines parallelization efficiency; currently tangled with dictionary grouping).

### 3. Schedule Emitter (Queue Management)
* **Boundary:** Packaging the ordered execution map into concrete `ExecutionGroup` layers, building the `ready_queues`, and producing the final immutable `ExecutionSchedule` and `SchedulingDiagnostics`.
* **Complexity:** Low (Simple factory/DTO translation logic).

## Conclusion
This decomposition isolates the "What" (Graph Analysis), the "How" (Policy Engine), and the "Result" (Schedule Emitter) to make the scheduler maintainable.
