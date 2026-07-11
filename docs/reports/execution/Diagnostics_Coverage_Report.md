# Diagnostics Coverage Report

## Current Coverage
- `omlx/runtime/scheduling/diagnostics.py` provides `SchedulingDiagnostics`.
- `omlx/runtime/execution/diagnostics.py` provides `ExecutionTimeline`, `BackendInvocationReport`, and `ExecutionReport`.
## Gaps
- Model loading, Capability Resolution, ExecutionPlan generation, LogicalIR, and PhysicalIR lack standardized immutable diagnostic snapshots integrated into a single framework.
