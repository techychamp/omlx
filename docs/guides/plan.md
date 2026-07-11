# ExecutionPlan Documentation

The `ExecutionPlan` is a frozen dataclass containing the blueprint for how a model should be executed.

### Core Attributes
- `execution_family`: The high-level model family (`AUTOREGRESSIVE`, `DIFFUSION`, etc.).
- `execution_backend`: The specific runtime backend (`autoregressive`, `speculative`, `diffusion`).
- `execution_mode`: The operational mode (`streaming` or `standard`).
- `execution_topology`: The physical distribution of the model (`single_node`).
- `cache_strategy`: The memory layout for caching (`paged`, `radix_tree`, etc.).
- `scheduler_strategy`: How requests should be batched (`continuous_batching`, `static_batching`).

### Pipeline Metadata
- `verification_stages`: Tuple of verification steps to run.
- `optimization_passes`: Tuple recording which optimization passes successfully mutated the plan.
- `execution_hints`: Arbitrary dictionary of backend-specific hints.
- `hardware_requirements`: Tuple of hardware constraints.
- `planner_metadata`: Diagnostic metadata (e.g., `planning_time_ms`).
