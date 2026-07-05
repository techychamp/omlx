# Extension Point Guide

Extension points are defined as Python `Protocol`s in `omlx.plugins.contracts`. To extend a specific behavior, a plugin must instantiate a class satisfying the protocol and register it.

## Available Extension Points
- **BackendPlugin**: Registers new physical execution backends.
- **PlannerPlugin**: Registers execution planning algorithms.
- **QuantizationPlugin**: Advertises support for specific weight quantizations (e.g., AWQ, GPTQ).
- **OptimizationPlugin**: Injects logical or physical IR passes.
- **ToolingPlugin / ExporterPlugin**: Injects debugging, visualization, or export tools (e.g., GraphViz).

## Using Extensions in Core
The Runtime should never import plugins directly. Instead:
```python
extensions = registry.get_extensions(BackendPlugin)
for ext in extensions:
    # Safely interact with extension capabilities
    pass
```
