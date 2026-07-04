# Validation Report

The `BackendValidationResult` has been expanded to validate not just operations, but specific backend metadata.

## Validation Targets
- `unsupported_operations`: Operations not natively supported by the backend.
- `unsupported_execution_families`: E.g., attempting a Diffusion graph on an Autoregressive-only backend.
- `unsupported_execution_modes`, `unsupported_capabilities`, `unsupported_optimizations`.
- `unsupported_quantization_formats`, `unsupported_precision_formats`.
- `missing_synchronization`, `missing_routing`, `missing_cache_strategies`.
