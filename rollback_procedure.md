# Rollback Procedure

- Disable the `COMPILER_RUNTIME_PIPELINE_ENABLED` feature flag via environment variable or CLI.
- No application restart is strictly required if using dynamic overrides, although a restart provides the cleanest fallback to legacy behavior.
- If necessary, revert the commits to `omlx/server.py` and remove `omlx/runtime/compiler_integration.py`.
