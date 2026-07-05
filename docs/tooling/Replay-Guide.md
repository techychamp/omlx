# Replay Framework Guide

The Replay Framework allows developers to capture `ReplaySession` objects containing compiler versions, diagnostics, feature flags, and outputs.

Using `CompilerReplay`, these sessions can be reloaded and simulated deterministically to verify compiler behaviors offline without invoking inference executions.

## Example Usage
```python
session = ReplaySession(
    compiler_version="1.0",
    planner_version="1.0",
    feature_flags=MappingProxyType({}),
    backend="mlx",
    optimization_pipeline=(),
    timestamps=MappingProxyType({}),
)
replay = CompilerReplay(session)
result = replay.replay()
```
