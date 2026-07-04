# Optimization Pipeline Guide

The `OptimizationPipeline` groups passes by `CompilerStage` (e.g., LOGICAL_IR).

## Execution Flow
1. Fetch ordered passes from the `PassManager`.
2. For each pass, check if it supports the pipeline's stage.
3. Apply the pass to the artifact.
4. Track diagnostics and execution statistics in the `OptimizationContext`.
5. Return the potentially mutated artifact. Passes must respect immutability invariants where applicable.
