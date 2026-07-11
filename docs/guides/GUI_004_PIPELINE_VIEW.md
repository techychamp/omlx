# GUI-004 Pipeline Visualization

## Strategy

The `CompilerPipelineView` visualizes the sequence of logical and physical phases that the oMLX compiler undergoes: Planning -> Logical IR -> Compiler Passes -> Physical IR -> Backend Translation -> Execution Graph.

## Implementation Details

The GUI renders this as an `HStack` of circular nodes connected by horizontal paths. Due to the GUI-002 API Freeze, we only have access to a singular `graphStatus` string from the `CompilerInspection` DTO, rather than fine-grained, step-by-step progress metrics. Consequently, the visualization is currently static, depicting the architectural phases without live progression animation.
