# Runtime Compiler Service Guide
The compiler is now a first-class service owned strictly by the Runtime instance (`RuntimeCompilerService`). It is never instantiated per-request and is instead reused across the lifecycle.

# Compiler Ownership Walkthrough
- `RuntimeBuilder` initializes the `RuntimeCompilerService`.
- `Runtime` owns `RuntimeCompilerService` and `CompilerSession`.
- `EnginePool` and `EngineCore` strictly handle execution and no longer construct `CompilerPipelineRunner`.
- `RuntimeContext` holds immutable artifacts populated by the pipeline runner.

# Dependency Injection Guide
- Dependencies are passed downwards via `Runtime` instantiation, eliminating scattered singleton access for compiler components.

# Thread Safety Report
- Handlers invoke `runtime.compiler_service.run_compilation()`. Internal operations depend entirely on stateless execution artifacts without polluting cross-request memory. The Runtime instance retains isolation correctly.

# Architecture & Repository Impact Report
- Feature flags correctly toggle stages without changing execution behavior. Legacy logic remains intact.

# Rollback Procedure
- Toggle off `OMLX_FEATURE_COMPILER_RUNTIME_PIPELINE` via environment to fall back to legacy discovery.

# Recommendations for MIG-005
- Decouple remaining Model Adapters into discrete lowering steps, ensuring IR boundaries are perfectly pure before execution.
