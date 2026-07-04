# Rollback Procedure

If the changes for MIG-002 cause regressions, use the feature flags to turn off the planner runtime:
- `export OMLX_FEATURE_EXECUTION_PLAN_RUNTIME=0`
- `export OMLX_FEATURE_EXECUTION_PROFILE_COMPATIBILITY=0`

The runtime will default to the legacy `ExecutionProfileRegistry`.
