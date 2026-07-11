# Exception Guide

The oMLX SDK provides a structured exception hierarchy for deterministic error handling.

## Hierarchy
*   `OmlxError`: Base exception for all SDK errors.
    *   `CompilerError`: Raised during translation or logical IR compilation failures.
    *   `PlanningError`: Raised if capabilities cannot be resolved or an execution plan cannot be formulated.
    *   `BackendError`: Raised when suitable backend hardware/adapters cannot be selected.
    *   `VerificationError`: Raised by the Verifier if critical thresholds or rulesets fail.
    *   `PluginError`: Raised when plugin loading or execution fails.
    *   `ConfigurationError`: General misconfiguration.
    *   `ValidationError`: General payload/request validation failure.
    *   `DiagnosticsError`: Raised when the diagnostic runner encounters system-level faults.

All exceptions provide detailed context strings. Internal exceptions (e.g. from `ExecutionPlanner`) are caught and wrapped in these public types.
