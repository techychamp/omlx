# Compiler Optimization Audit

## Overview
Currently, optimization in the oMLX compiler is scattered and hardcoded. The compiler phases are defined as:
`CapabilityResolver -> ExecutionPlanner -> Logical IR -> Lowering -> Physical IR -> Backend Translation`

## Audit Findings
- **ExecutionPlanner**: Contains hardcoded backend and mode selection based on capabilities (`omlx/planner/planner.py`).
- **Passes**: Existing passes like `omlx/planner/passes.py` (which just modified a dict) and `omlx/planner/compiler/passes.py` lacked a generic, multi-stage Pass Manager and clear separation of concerns (Analysis vs Optimization).
- **Caches**: Exist in `omlx/compiler_perf/cache.py` but are not integrated into a generic optimization framework.

## Path Forward
The new generic Optimization Framework in `omlx/optimization/` standardizes passes across all stages of compilation (CapabilityDescriptor, ExecutionPlan, LogicalIR, PhysicalIR, BackendOperationGraph).
