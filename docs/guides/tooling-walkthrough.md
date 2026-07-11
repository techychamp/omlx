# Compiler Developer Toolkit Walkthrough

## Introduction
The oMLX Compiler Developer Toolkit (TOOLING-001) provides a comprehensive, strictly read-only suite of tools for inspecting, exporting, comparing, and tracing the compiler's internal states.

## Key Features
1. **Inspector**: Inspect `CapabilityDescriptor`, `ExecutionPlan`, and IR graphs as Python dicts.
2. **Exporters**: Convert compiler artifacts to JSON, YAML, GraphViz, Mermaid, PlantUML, and Markdown.
3. **Diff Tool**: Compare plans and IRs to identify structural and metadata regressions.
4. **Tracer**: Profile compiler passes and record diagnostics.
5. **CLI**: Access introspection tools from the command line (`omlx-tooling`).

## Getting Started
To inspect an execution plan:
```python
from omlx.tooling.inspector.inspector import CompilerInspector
inspector = CompilerInspector()
data = inspector.inspect_execution_plan(plan)
```

To export an IR to Mermaid:
```python
from omlx.tooling.export.mermaid_exporter import MermaidExporter
from omlx.tooling.views.graph_views import to_value_graph
exporter = MermaidExporter()
graph_data = to_value_graph(ir)
print(exporter.export(graph_data))
```
