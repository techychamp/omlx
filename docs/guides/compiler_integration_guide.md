# Compiler Integration Guide

The Fusion Planning domain integrates directly with the `CompilerPlanner`.

`CompilerPlanner.compose_bundle` now performs the following steps:
1. Orchestrates existing domains (e.g. Memory Planner).
2. Reads the `GraphDescriptor`, `DependencyGraph`, and `GraphAnalysisReport` from the overarching context.
3. Invokes `FusionPlanner.plan(...)` to generate a `FusionPlan`.
4. Adds the `FusionPlan` to the `PlanningBundle`.

The Compiler Planner maintains an execution-independent relationship with fusion, acting only as the orchestration layer for the artifacts.
