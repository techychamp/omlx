# Compiler Trace Documentation

The `CompilerTracer` provides zero-overhead observability into the compiler pipeline when enabled.

## Features
- **Timing**: Use `with tracer.trace_pass("pass_name")` to accurately time lowering or optimization passes.
- **Diagnostics**: Store custom non-fatal error messages or observations during compilation.
- **Reporting**: Traces can be fed into the `DiagnosticsDashboard` to generate aggregate statistics (e.g., total duration, cache hits).

## Constrains
The tracer is read-only. It does not modify the execution path or the compiler artifacts it measures.
