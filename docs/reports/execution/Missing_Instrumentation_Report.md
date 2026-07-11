# Missing Instrumentation Report

## Missing Telemetry & Tracing
- **Model**: No standard trace for model initialization.
- **Capability Resolution**: Needs tracing for capability merges and fallbacks.
- **ExecutionPlan / LogicalIR / PhysicalIR**: Missing timing, memory estimates, and artifact tracking APIs.
- **BackendAdapter**: Needs latency and dispatch time tracing.
- **Storage/Export**: No unified bundle exporter (`observation_bundle/`).
- **Thread Safety**: Current `CompilerTracer` uses a simple thread-local or global state that needs to be replaced with a purely functional/immutable or properly isolated concurrent observer design.
