# MEMORY-001: Compiler-Native Planning Domains, Memory Planning Framework & Tensor Lifetime Architecture

## Architecture Changes
- Introduced `PlanningBundle` as a core artifact that coordinates output from multiple planning domains.
- Established `MemoryPlanner` inside `omlx/planner/domains/memory/planner.py` to handle memory planning without executing or allocating memory.
- Created immutable `MemoryDescriptor`, `TensorLifetime`, `MemoryRequirement`, `MemoryPlan`, `AllocationGraph`, `LifetimeGraph`, `MemoryCompatibilityReport`, `MemoryValidationReport`, and `MemoryStatistics` in `artifacts.py`.
- Updated `CompilerPlanner` to compose the `execution_plan` and `memory_plan` into the `PlanningBundle`.
- Refined `ExecutionContext` to include the `planning_bundle` to correctly propagate planning down the execution pipeline.
- Established `RuntimeSession` to coordinate the `PlanningBundle` lifecycle inside `omlx/runtime/session.py`.

## Implementation Summary
The Compiler now orchestrates the `ExecutionPlanner` and `MemoryPlanner`, bundles their artifacts into a single `PlanningBundle`, and passes them successfully into the Execution Engine pipeline, keeping the backend entirely memory-planning agnostic. `GenerationStrategy` was augmented with `strategy_intent` to express memory requests correctly to the `MemoryPlanner`. Type errors in the API representations around `ConfigDict` and missing PyDantic requirements in test dependencies were also handled. Tests were heavily updated to extract `.execution_plan` from the bundled returns where appropriate.

## Test Results
Passed all relevant unit and architecture tests for planner (`pytest tests/planner/`), tooling (`pytest tests/tooling/`), and reliability (`pytest tests/test_reliability/`). The test failures remaining are associated with missing external dependency imports such as `mlx_vlm`, `safetensors`, `huggingface_hub`, and `fastapi.testclient`, which are unrelated to `MEMORY-001` changes.

## Known Issues
- Full repository test suite failures strictly due to external testing library imports (`pytest` plugins, `fastapi`, `huggingface_hub`, etc.) that are unsupported in the restricted CI setup.
