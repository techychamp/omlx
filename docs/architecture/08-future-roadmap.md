# Future Roadmap & Abstractions

This roadmap reorients the architecture away from feature-specific backends and towards a generalized Execution Planning Layer.

## The Target Abstraction Chain

Rather than building a new backend for every model architecture, future integrations must follow this abstraction chain. Models become consumers of execution modes, not drivers of them.

1. **Capabilities**: Declared by the model via `CapabilityRegistry`.
2. **Execution Planner**: A new architectural component that analyzes capabilities and request contexts.
3. **Execution Plan**: The output of the planner.
4. **Execution Graph**: The structural representation (`PREFILL`, `FORWARD`, `VERIFY`, `DENOISE`).
5. **Backend**: The low-level execution engine (e.g., `AutoregressiveBackend`, `DiffusionBackend`).

*Note: The Scheduler remains completely agnostic. It accepts requests and a `SchedulingPolicy`. The Execution Planner may dictate the policy, but the Scheduler does not plan execution.*

## Revised 10-Phase Roadmap

### Phase 0: Repository Constitution ✅
* Establish base engineering principles and constraints (`AGENTS.md`).

### Phase 1: Architecture Handbook ✅
* Complete runtime discovery, ownership mapping, and baseline documentation (`docs/architecture/`).

### Phase 2: Execution Planning Layer
* Introduce the **Execution Planner**.
* Determine where it lives and how it bridges Capabilities to Execution Graphs without modifying `EngineCore` or `Scheduler`.
* This is a design phase (RAES-003).

### Phase 3: Execution Programs
* Implement the core execution primitives as plans:
  * Autoregressive (AR)
  * Diffusion
  * Verification
  * Mixture of Experts (MoE)

### Phase 4: Nemotron Integration
* Consume the Execution Planning layer to support Nemotron models.

### Phase 5: HF Validation
* Validate end-to-end integration with HuggingFace Hub loading.

### Phase 6: Diffusion Gemma Integration
* Consume the Diffusion execution program.

### Phase 7: Triage
* Implement conditional verification execution plans.

### Phase 8: Streaming MoE
* Implement MoE execution programs **in Python** to prove the architecture.

### Phase 9: Optimization
* Push proven bottlenecks (e.g., Streaming MoE) down into custom Metal kernels (C++).
