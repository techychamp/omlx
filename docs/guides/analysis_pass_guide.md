# Analysis Pass Guide

`AnalysisPass` instances do not modify the compiler artifact. They inspect the artifact and report findings via diagnostics or metadata attached to the context.

## Implementation Requirements
- Must inherit from `AnalysisPass`.
- Must implement the `analyze(self, artifact, context)` method.
- Must be stateless and deterministic.
