# Ownership Report

- **Runtime**: Owns request lifecycle, session lifecycle, and execution coordination. Does NOT own batching policy.
- **Planning**: Owns request compatibility, batch composition, and resource requirements through the deterministic `BatchPlanner`.
- **Compiler**: Owns `BatchPlan` generation and composition, producing immutable batch descriptions without executing.
- **GenerationStrategy**: Owns execution intent and policy via `BatchGenerationStrategy`.
- **Scheduler**: Owns dependency and execution ordering.
- **ExecutionEngine**: Consumes `PlanningBundle` (including `BatchPlan`) to execute.
- **Backend**: Executes operations, unaware of batching.
- **Observability**: Passively records metrics.
- **API**: Exposes configurations.
- **Tooling**: Inspects artifacts.
