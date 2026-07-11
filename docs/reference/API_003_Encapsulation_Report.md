# API-003 Encapsulation Report

## Encapsulation Status

-   **Runtime**: Fully encapsulated. Public API interacts through `RuntimeService`. `omlx.runtime` classes are hidden.
-   **ExecutionEngine**: Hidden behind `CompilerService` and `RuntimeService`.
-   **ExecutionDispatcher**: Not exposed.
-   **BackendAdapter**: Handled entirely inside `BackendManager` and internal registries.
-   **GraphScheduler**: Not exposed in API layer.
-   **CompilerPipelineRunner**: Hidden by `CompilerService`.
-   **LogicalIR / PhysicalIR**: Removed from public API signatures.
-   **CompilerSession**: Hidden.

No internal implementation types appear in the public API `__init__.py`.
