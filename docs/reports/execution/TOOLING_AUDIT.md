# Compiler Tooling Audit

## Current State
The current compiler pipeline executes `CapabilityResolver` -> `ExecutionPlanner` -> `Logical IR` -> `LoweringEngine` -> `Physical IR` -> `Backend Adapter`.

## Observability Gaps
Currently, developers cannot inspect the intermediate states of the compiler easily:
1. `CapabilityDescriptor`: The output of `CapabilityResolver` cannot be directly dumped or visualized in a standardized way.
2. `ExecutionPlan`: The `ExecutionPlanner` output is immutable but lacks utilities for JSON export or visualization of the planned layout.
3. `Logical IR` & `Physical IR`:
    - Cannot be visualized as graphs.
    - No diff tools to compare IR before and after passes.
4. Pass Execution & Lowering:
    - No tracing mechanism for pass durations.
    - No tracing of what nodes were modified.
    - Cache hit/miss statistics are not easily exportable.
5. `Backend Graph`:
    - Cannot be exported for debugging without changing runtime code.

## Required Tooling (TOOLING-001)
- `CompilerInspector`: Read-only views of intermediate objects.
- Graph Exporters: JSON, YAML, GraphViz, Mermaid, PlantUML.
- Tracing & Profiling: Read-only compiler timing and event tracing.
- CLI: Expose introspection and validation tools for developers.
