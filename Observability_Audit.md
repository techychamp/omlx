# Observability Audit

This document audits existing logging, statistics, tracing, reports, visualizations, and timelines across the runtime and compiler.

## Findings
- **Logging**: Pervasive `import logging` used across the codebase, but often prints unstructured data.
- **Statistics**: Existing `SchedulingStatistics` and `ExecutionStatistics` capture some data, but lack unified telemetry tracking.
- **Tracing**: Basic tracing exists in `omlx/tooling/trace/tracer.py` (`CompilerTracer`) and `omlx/tooling/replay/timeline.py` (`CompilerTimeline`), but it's not integrated end-to-end.
- **Reports/Visualization**: Some mermaid export exists in `InteractiveTrace.export_mermaid()`, but no comprehensive graph visualization (e.g. Graphviz DOT for BackendOperationGraph).
