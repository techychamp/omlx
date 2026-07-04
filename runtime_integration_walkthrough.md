# Runtime Integration Walkthrough

## Pipeline Setup
We introduce a `CompilerPipelineRunner` (in `omlx.runtime.compiler_integration`) which acts strictly as an orchestrator. It is injected with a `Runtime` instance and fetches the existing subsystems:
1. `CapabilityResolver`
2. `ExecutionPlanner`
3. `LoweringEngine`
4. `AdapterRegistry`

## Granular Feature Flags
Migration occurs smoothly through granular feature flags:
- `COMPILER_RUNTIME_PIPELINE_ENABLED`: Master toggle.
- `CAPABILITY_RUNTIME_ENABLED`: Runs `CapabilityResolver`.
- `PLANNER_RUNTIME_ENABLED`: Runs `ExecutionPlanner` (depends on capabilities).
- `LOWERING_RUNTIME_ENABLED`: Lowers to `PhysicalIR` (depends on planner).
- `ADAPTER_RUNTIME_ENABLED`: Translates to `BackendOperationGraph` (depends on physical IR).

## Endpoint Integration
In endpoints like `/v1/completions` and `/v1/chat/completions`, right after acquiring the engine lease and validating context window lengths, we query the feature flags and optionally execute the `CompilerPipelineRunner`. The output `TranslationResult` is logged and diagnostics are recorded, while the legacy request flow proceeds unmodified.
