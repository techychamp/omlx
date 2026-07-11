# Runtime Planning Audit

## Locations Analyzed
- `omlx/inference/execution_profile.py`: Defines `ExecutionProfile` and `ExecutionProfileRegistry`. Planning logic resides in `_default_resolver` (hardcoded model strings).
- `omlx/engine_core.py`: Initializes the registry and calls `resolve()`.
- `omlx/scheduler.py`: Consumes `ExecutionProfile` indirectly or directly (actually, strategy receives backend, engine, scheduler).
- `omlx/planner/planner.py`: Defines `ExecutionPlanner` and `ExecutionPlan`.

## Planning Logic Duplication
- `ExecutionProfileRegistry` duplicates backend selection logic that belongs in `ExecutionPlanner`.
- Capability resolution in `engine_core.py` (via `infer_capabilities` and `ActualCapabilities`) overlaps with `CapabilityResolver`.

## ExecutionPlan Replacement
- `ExecutionPlan` will replace the `ExecutionProfileRegistry.resolve()` call in `engine_core.py`.
- `ExecutionProfile` will be generated from `ExecutionPlan` using a new `ExecutionProfileAdapter`.
