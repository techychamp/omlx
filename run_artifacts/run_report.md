# RUN-001 — First Real Compiler-Driven Model Execution

## Summary

| Phase | Status | Duration |
|---|---|---|
| Phase A — Compiler Pipeline | PASSED | 0.26 ms pipeline + 0.085 ms engine |
| Phase B — Real Inference    | PASSED | 95 ms load + 118 ms inference |
| Total harness duration      | — | 2.13 s |

## Generated Output

**Model:** `mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit`  
**Prompt:** `The capital of France is`  
**Generated:** `Paris. The capital of France is Paris. The`  
**Token count:** 11  
**Temperature:** 0.0 (deterministic)  

## Compiler Pipeline Walkthrough

```
Model ID  (TinyLlama-1.1B)
  ↓
CapabilityResolver.resolve()     → CapabilityDescriptor
  ↓
ExecutionPlanner.plan()          → ExecutionPlan
  ↓
IRBuilder.build()                → LogicalIR (ExecutionIR)
  ↓
LoweringEngine.lower()           → PhysicalIR
  ↓
MLXAdapter.translate()           → TranslationResult + BackendOperationGraph
  ↓
ExecutionEngine.execute()        → DeterministicGraphExecutor
  ↓
GraphScheduler.build_schedule()  → ExecutionSchedule
  ↓
SequentialExecutionDispatcher    → per-operation dispatch
  ↓
MLXAdapter.execute() × 5         → structural mock (BACKEND-005 pending)
```

## Phase A — Compiler Artifacts

**CapabilityDescriptor**
- execution_family   : `autoregressive`
- supports_streaming : `True`
- attention_types    : `('causal',)`

**ExecutionPlan**
- execution_family   : `autoregressive`
- execution_backend  : `autoregressive`
- execution_mode     : `streaming`
- scheduler_strategy : `continuous_batching`

**BackendOperationGraph**
- backend_id  : `mlx`
- operations  : `['node_prefill', 'node_sample', 'node_forward', 'node_verify', 'node_emit']`
- roots       : `('node_emit',)`

**ExecutionStatistics**
- executed_operations       : `5`
- backend_invocations       : `5`
- adapter_calls             : `5`
- execution_duration_ms     : `0.056 ms`
- compiler_execution_count  : `1`
- legacy_fallback_count     : `0`

## Phase B — Real Inference Shim

Phase B calls `mlx_lm.generate()` directly from the harness, **not** via
`MLXAdapter.execute()`. This preserves the architectural boundary for BACKEND-005.

## Known Limitations

- `MLXAdapter.execute()` is a structural mock; real kernel dispatch is BACKEND-005.
- Phase A compiler plan uses a synthetic model label (no weight loading in compiler).
- Phase B inference (mlx_lm.generate) is a compatibility shim, not compiler-driven decode.

## Recommendations

- BACKEND-005: Implement real MLX forward kernel dispatch in `MLXAdapter.execute()`.
- Bridge Phase A and Phase B by injecting the loaded model into `ExecutionContext.model`.
- Add a streaming decode loop driven by the compiler's `ExecutionSchedule`.

## Artifact Index

| File | Contents |
|---|---|
| `model_descriptor.json` | Model identification record |
| `capability_descriptor.json` | CapabilityDescriptor from resolver |
| `execution_plan.json` | ExecutionPlan from planner |
| `logical_ir.json` | LogicalIR from IRBuilder |
| `physical_ir.json` | PhysicalIR from LoweringEngine |
| `backend_operation_graph.json` | BackendOperationGraph from MLXAdapter |
| `translation_result.json` | Full TranslationResult with diagnostics |
| `execution_schedule.json` | ExecutionSchedule diagnostics |
| `statistics.json` | ExecutionStatistics |
| `diagnostics.json` | Error/diagnostic summary |
| `compiler_session.json` | CompilerSession lifecycle record |
| `compiler_statistics.json` | RuntimeCompilerService statistics |
| `runtime_context.json` | Runtime context snapshot |
| `execution_context.json` | ExecutionContext snapshot |
| `run_report.md` | This report |