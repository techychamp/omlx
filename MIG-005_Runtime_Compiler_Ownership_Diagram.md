# Runtime Compiler Ownership Diagram

The following diagram illustrates the compiler ownership and execution flow for oMLX requests post MIG-005:

```text
User Request
   │
Server (omlx/server.py)
   │ (Delegates execution)
Runtime (omlx/runtime/builder.py)
   │ (execute_request)
RuntimeCompilerService (omlx/runtime/compiler_service.py)
   │
CompilerPipelineRunner
   │
ExecutionPlan
   │
LogicalIR
   │
PhysicalIR
   │
BackendOperationGraph
```

The Server and EnginePool no longer invoke planning logic, acting strictly as orchestrators/consumers of the underlying abstractions managed by the RuntimeCompilerService.
