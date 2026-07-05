# Rollback Guide

If the ExecutionEngine experiences failures:
1. Ensure the feature flag `OMLX_FEATURE_COMPILER_RUNTIME_ENABLED` is set to `0`.
2. Set `OMLX_FEATURE_LEGACY_RUNTIME_ENABLED` to `1` to route intents safely.
