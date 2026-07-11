# Placement Report

The Placement framework models device constraints for tensor dispatch logic using placement optimizations (`AppleDeviceOptimizationPass` -> `AppleOptimizationPolicy`).
The design successfully shifts specific deployment overrides into `OptimizationStatistics` and `OptimizationDiagnostics`, preventing pollution of the abstract `ExecutionEngine`. Placement optimizations modify the metadata on the `PlanningBundle` safely without direct state mutation, matching strictly defined immutable artifact guidelines.
