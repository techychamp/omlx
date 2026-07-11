
# Batch Realization Architecture Audit

## 1. Goal
Implement compiler-native batch realization.
Batch Planning describes batch parameters (BatchPlan), and the Compiler realizes this plan into an executable batch graph (BatchExecutionGraph).

## 2. Ownership
- **Batch Planning**: Owns the rules, logic, constraints, and strategy of batching via `BatchPlan`.
- **Compiler**: Owns the realization (generation) of `BatchExecutionGraph` from `BatchPlan`.
- **RuntimeSession**: Owns session execution metadata. Added attributes for `batch_execution_graph` and `batch_realization_report`.
- **Scheduler**: Continues to own deterministic dependency scheduling without being aware of batch logic.
- **Execution Engine**: Consumes `BatchExecutionGraph` and executes it.
- **Backend**: Executes operations blindly, unaware of grouping, synchronization, or batch boundaries.

## 3. Implemented Components
- `BatchExecutionGraph`, `BatchGroupingGraph`, `BatchSynchronizationGraph` added in `omlx/planner/compiler/batch/artifacts.py`
- `BatchRealizationReport`, `BatchRealizationStatistics`, `BatchRealizationDiagnostic` added in `omlx/planner/compiler/batch/artifacts.py`
- `BatchRealizer` implementation inside the Compiler that deterministically transforms `BatchPlan` into execution artifacts.
- `Compiler.realize_batch(plan)` added.
- `RuntimeSession` updated to attach batch realization artifacts.

## 4. Tests
- Tests confirm that batch realization happens effectively within the compiler boundary.
- Next step is to implement tooling to observe the realization graphs.
