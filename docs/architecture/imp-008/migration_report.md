# Migration Report - Fusion Planning

This document details the migration path to compiler-native Fusion Planning.

## Additions
- `FusionPlan`, `FusionGroup`, `FusionOpportunity`, and diagnostic structures.
- `FusionAnalyzer` and `FusionPlanner`.

## Refactoring
- `PlanningBundle` updated to include an optional `fusion_plan`.
- `CompilerPlanner` updated to coordinate Fusion Planning.

## Impact
No execution strategies, kernels, or existing runtime operations have been mutated or overwritten. Observability can track `FusionStatistics` from the bundle, and tooling can parse it statically.
