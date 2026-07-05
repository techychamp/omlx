# Runtime Migration Audit
## Runtime Migration Phase
In MIG-003, the execution intent generation has been officially separated from `EngineCore` and migrated to the `EnginePool`.

### Scheduler
The `Scheduler` remains identical and continues to dictate loop scheduling. It consumes `Request`s directly. In MIG-004, the plan is to align the Scheduler's loop to consume logical operations from the `BackendOperationGraph` rather than handling execution natively.

### EnginePool
`EnginePool` has been updated to host the `CompilerPipelineRunner`. When an engine is requested via `get_engine`, the pipeline is executed before the actual backend loads. This creates explicit isolation of the compilation vs loading boundaries, positioning `EnginePool` as the runtime component holding execution metadata.

### Backend Interfaces
`BackendFactory` currently consumes an `ExecutionProfile` to build the required execution backend. Moving forward, the `ExecutionPlan` from the compiler should supplant the `ExecutionProfile`, and backends will interface directly with the `Physical IR` generated during the pipeline.
