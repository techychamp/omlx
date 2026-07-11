# Migration Risk Report

- **Performance Overhead**: Compiling the pipeline dynamically adds some latency overhead to every request. Monitored through `planner_metadata`.
- **Exceptions**: Unhandled exceptions in the new compiler pipeline could halt the legacy flow if not properly wrapped in `try/except`.
- **Thread Safety**: The `CompilerPipelineRunner` accesses global registries and resolvers. All referenced components must guarantee thread-safety (which they do by being immutable after bootstrapping).
