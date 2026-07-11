# Fusion Planning Guide

The oMLX compiler integrates a dedicated Planning Domain for Fusion, known as `FusionPlanner`. The Fusion Planning domain is responsible for analyzing the `GraphDescriptor` and `DependencyGraph` using the `GraphAnalysisReport` to discover and validate fusion opportunities without manipulating execution behavior.

## Core Concepts

1. **Analyzer**: `FusionAnalyzer` reads the `GraphAnalysisReport` and `DependencyGraph` to identify potential nodes to fuse (`FusionOpportunity`).
2. **Validator**: `FusionValidator` ensures proposed fusions reference existing operations in the `DependencyGraph`.
3. **Planner**: `FusionPlanner` generates an immutable `FusionPlan` artifact.

## Integration

The `FusionPlanner` is instantiated and executed by the `CompilerPlanner`. Its output, `FusionPlan`, is stored inside the global `PlanningBundle`.
