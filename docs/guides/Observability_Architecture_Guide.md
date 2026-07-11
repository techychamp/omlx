# Observability Architecture Guide

The Observability framework provides a passive, read-only window into the compiler and execution runtime. It relies on the `Observer` pattern to collect `ExecutionTrace`, `TelemetrySnapshot`, and `ArtifactBundle` without mutating state.
