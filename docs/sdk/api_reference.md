# API Reference (v1)

This document provides a reference for the `omlx.api.v1` namespace.

## Builders
*   **`RuntimeBuilder`**: Fluent builder for creating a `Runtime` instance.
*   **`CompilerRequestBuilder`**: Fluent builder for creating a `CompilerRequest`.
*   **`PlanningRequestBuilder`**: Fluent builder for creating a `PlanningRequest`.
*   **`BackendRequestBuilder`**: Fluent builder for creating a `BackendRequest`.
*   **`VerificationRequestBuilder`**: Fluent builder for creating a `VerificationRequest`.

## Services
*   **`Runtime`**: The central runtime instance.
*   **`Compiler`**: Compiles logical IR into physical IR using `CompilerEngine`.
*   **`Planner`**: Resolves capabilities into execution plans using `ExecutionPlanner`.
*   **`BackendManager`**: Handles target execution capability selections.
*   **`Inspector`**, **`Verifier`**, **`PluginManager`**, **`PerformanceMonitor`**, **`DiagnosticsRunner`**, **`ToolingManager`**: Core sub-services.

## Exceptions
*   `OmlxError` (Base)
*   `CompilerError`, `PlanningError`, `BackendError`, `VerificationError`, `PluginError`, `ConfigurationError`, `ValidationError`, `DiagnosticsError`.
