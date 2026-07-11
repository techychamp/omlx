# MIG-005 Execution Ownership Guide

## Architectural Invariants
With the completion of MIG-005, the following invariants strictly govern the execution pipeline:
- **Server:** Responsible only for request validation, acquiring the runtime, and triggering execution. It must **never** orchestrate compilation logic.
- **Runtime:** Owns subsystems including the `RuntimeCompilerService`. Exposes an `execute_request()` orchestrator.
- **RuntimeCompilerService:** The exclusive owner of the `CompilerPipelineRunner`.
- **EnginePool:** Acts solely as a consumer of compiler artifacts and loaded engines, managing physical limits but never deciding *how* or *when* execution planning occurs.

## Configuration & Feature Flags
- `COMPILER_RUNTIME_ENABLED`: Triggers compilation when `Runtime.execute_request()` runs.
- `PRIMARY_COMPILER_EXECUTION`: Marks the compiler pipeline as the dominant execution planner (artifacts produced).
- `COMPILER_COMPATIBILITY_MODE`: Ensures Legacy Engine paths operate seamlessly while generating compiler artifacts in the background.

## Migration Path to EXEC-001
This architectural shift completely decouples planning from legacy execution, meaning EXEC-001 simply needs to wire the `BackendOperationGraph` directly into the `BackendAdapter`'s `execute` API, bypassing the legacy `BatchedEngine`.
