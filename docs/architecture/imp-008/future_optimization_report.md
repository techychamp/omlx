# Future Optimization Report

By separating Fusion Planning from Backend execution and Graph formulation, the following optimizations become natively supported without architectural changes:
- Distributed Execution: The `FusionPlan` can be sliced alongside the `DependencyGraph`.
- MoE: Sub-graphs can be fused conditionally per expert.
- Apple Silicon Optimization: Specific fusion targets (e.g., grouped query attention on Metal) can be identified in analysis and dispatched.
