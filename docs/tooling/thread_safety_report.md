# Thread Safety Report
All tooling classes (`CompilerInspector`, `JsonExporter`, `CompilerDiffer`) are stateless. Trace and view helpers do not mutate the input objects. They are inherently thread-safe for parallel execution.
