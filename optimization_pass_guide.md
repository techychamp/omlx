# Optimization Pass Guide

`OptimizationPass` instances can modify the compiler artifact (e.g., returning a new, optimized version).

## Implementation Requirements
- Must inherit from `OptimizationPass`.
- Must implement the `apply(self, artifact, context)` method.
- Must not change inference semantics.
- Should track its own statistics (e.g., nodes removed).
