# Glossary

*   **Adapter:** Short for `ModelAdapter`. Contains model-specific behavior and provides immutable configuration parsing.
*   **Backend Operation Graph:** A Directed Acyclic Graph (DAG) of backend-specific operations generated during Translation.
*   **CapabilityDescriptor:** A deeply immutable, nested object modeling full execution behavior and features of a model, consumed by the ExecutionPlanner.
*   **Compiler Pass:** An atomic unit of logic in the `PassManager` (Analysis, Rewrite, or Validation) that inspects or transforms Execution IR.
*   **EnginePool:** The highest-level manager in the runtime, owning memory and model lifetimes.
*   **Execution Backend:** Orchestrates pipelines and execution flow, executing backend-specific code (e.g., Metal, MLX).
*   **ExecutionPlan:** An immutable dataclass generated deterministically by the `ExecutionPlanner` representing the execution strategy.
*   **Feature Flag:** Ephemeral toggles prefixed with `OMLX_FF_` used to safely gate in-flight capabilities during runtime boot.
*   **IRNode:** A single node in the ExecutionIR DAG representing an atomic step (e.g., Prefill, Sample).
*   **Logical IR:** The high-level semantic representation of an execution request's data flow.
*   **Lowering:** The process of converting Logical IR down to hardware-agnostic Physical IR.
*   **Physical IR:** A backend-agnostic representation of operations ready for Translation.
*   **Registry:** A strictly-typed, immutable (post-boot) collection of extensions, adapters, or capabilities.
*   **Runtime:** The central application object produced by the `RuntimeBuilder` (Composition Root) that owns all subsystems.
*   **Scheduler:** The execution-agnostic component responsible for queueing, batching, and memory constraints.
*   **TranslationResult:** The final output of the Adapter Framework translating Physical IR into a Backend Operation Graph.
