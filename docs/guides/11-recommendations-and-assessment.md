# Architecture Recommendations & Assessment

## Architecture Recommendations

1. **Implement an Execution Planning Layer**: The current architecture jumps directly from Capabilities to Execution Backends. We recommend inserting an `ExecutionPlanner` that takes Model Capabilities, generates an `ExecutionPlan`, which outputs an `ExecutionGraph`, which is then run by the `Backend`. This allows models (like Nemotron or Diffusion Gemma) to become consumers of execution modes, preventing an explosion of custom backends.
2. **Keep the Scheduler Dumb**: The `Scheduler` should remain purely focused on scheduling (batching, memory bounds, IOKit synchronization). Do not implement dynamic execution strategies inside the Scheduler. Instead, the `ExecutionPlanner` should dictate the `SchedulerPolicy`.
3. **Decouple Scheduler from `BatchGenerator`**: The Scheduler currently relies heavily on `mlx-lm`'s internal `BatchGenerator`. To support more exotic execution plans, OMLX should define its own abstract execution node runner interface.
4. **Python-First Optimization Strategy**: Features like Streaming MoE should first be proven in pure Python within the new Execution Planner abstraction. Only once the architecture is proven should performance bottlenecks be pushed down into custom C++ Metal kernels.

## GO / NO-GO Assessment

**Decision**: **GO**

**Justification**:
The repository architecture is well-structured, discoverable, and successfully implements complex concepts like continuous batching and Paged SSD caching on top of MLX.
* Critical runtime ownership between `EnginePool`, `EngineCore`, and `Scheduler` is clear and verifiable via the codebase.
* The `Scheduler` already supports `SchedulingPolicy`, which perfectly positions the architecture for an Execution Planner layer.
* Testing coverage is high, particularly for the core scheduler and cache components, providing a strong safety net for future development.

No major architectural contradictions were discovered. The path forward is clear: perform a design audit for the Execution Planner (RAES-003) before commencing implementation.
