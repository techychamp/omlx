# Verification Guide

## 1. Overview
The oMLX Verification Framework ensures that the engine produces mathematically equivalent results to reference implementations (like HuggingFace), adheres to strict performance budgets, and strictly complies with the system architecture.

Verification is treated as an isolated domain; a verification failure aborts the boot process to prevent the server from taking traffic in an unsafe state.

## 2. Scientific Verification Framework
The core of inference verification relies on:
*   **Golden Tests:** Executing deterministic prompts against known model weights with fixed seeds, asserting exact token-for-token output matches.
*   **HuggingFace Equivalence:** Ensuring that the generation logic (and custom MLX implementations of Attention, MoE, etc.) perfectly mirrors the reference PyTorch models.

## 3. Regression Framework
The CI pipeline runs automated checks against regressions.
*   **Performance Regression:** Ensures throughput, latency, and memory utilization do not slip beyond established budgets.
*   **Migration Verification:** Validates that as legacy execution paths are removed, the new Compiler Pipeline produces the exact same Physical IR operations.

## 4. Architectural Fitness Functions
Instead of relying solely on code review, oMLX uses **Architectural Fitness Functions** integrated into the CI pipeline via static analysis (e.g., using `pytest` AST parsing) to guarantee RAES-015 compliance:
1.  **Dependency Violations:** No imports from `omlx.server` inside `omlx.inference`.
2.  **Scheduler Isolation:** The Scheduler must never import MLX model implementations or registries directly.
3.  **Adapter Encapsulation:** `EngineCore` cannot instantiate adapters directly; it must use the Adapter Resolver.
4.  **Plugin Restrictions:** Plugins cannot modify Scheduler or ExecutionEngine instances.
5.  **Registry Freezing:** The Capability Registry must throw an `ImmutableError` if mutated after startup.

## 5. Thread Safety & Validation
Validation tools enforce strict thread boundaries to prevent data races. The defined ownership chain is:
`HTTP Thread (I/O, non-blocking) -> Engine Thread (Scheduler, triggers execution) -> MLX Thread (C++/Metal execution, invoked only from Engine Thread) -> Background/Metrics Threads.`

Capabilities validate against an extensible, rule-based architecture (`ValidationRule`, `ValidationRegistry`, `ValidationEngine`). All validation rules must be entirely stateless, independently defined, and must not mutate descriptors or cache mutable data to ensure thread-safety.
