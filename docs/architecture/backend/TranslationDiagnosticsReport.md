# Translation Diagnostics Report

Translation from PhysicalIR to Backend-Native Operations now tracks rich diagnostics inside `TranslationResult`.

## Data Collected
- `translation_latency`: Time spent (in seconds) translating the graph.
- `operation_statistics`: Count of generated backend-native operations (e.g. 5 `MLXForwardOperation`).
- `graph_statistics`: Metric data such as total nodes and edges in the compiled dependency graph.
- `fallback_decisions`: Decisions made when an operation is partially unsupported.
- `translation_metadata`: Information about the active adapter and its version.
- `warnings` & `diagnostics`: Developer and operational logs for debugging graph compilation issues.
