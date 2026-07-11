# Batch Realization Guide

## Process Overview
1. A request queue generates a `BatchPlan` via the Batch Planner.
2. The `BatchPlan` is passed to the Compiler.
3. The Compiler's `BatchRealizer` generates a `BatchExecutionGraph`.
4. The `BatchExecutionGraph` is attached to a `RuntimeSession`.
5. The Execution Engine consumes the `BatchExecutionGraph`.
