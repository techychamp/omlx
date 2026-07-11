# Tooling Audit & Developer Guide

## Audit Report
- The Tooling Framework (`omlx/tooling/framework/`) has been created.
- The Runtime, Compiler, Execution, and Backend Inspectors (`omlx/tooling/inspector/`) are unified and use read-only semantics.
- Snapshot Support (`omlx/tooling/snapshot/`) and Benchmark Helpers (`omlx/tooling/benchmark/`) provide passive observability integrations.
- All tools ensure that Runtime execution paths are never mutated.

## Guidelines
- All tools are thread-safe and stateless.
- Plugins can register extra tools via `ToolingPluginManager`.
- Use the central entry point: `get_tooling()` for accessing the tools.
