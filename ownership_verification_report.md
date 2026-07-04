# Ownership Verification Report

- **Runtime**: Owns `CapabilityResolver`, `ExecutionPlanner`, `LoweringEngine`, `AdapterRegistry`, `BackendDescriptorRegistry`.
- **EnginePool**: Owns `EngineCore`, `Schedulers`, model lifetimes, memory.
- **CompilerPipelineRunner**: Orchestrator only. It does not own or instantiate any core components. It simply coordinates their execution based on the request configuration.
