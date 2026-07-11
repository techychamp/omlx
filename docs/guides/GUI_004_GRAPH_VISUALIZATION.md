# GUI-004 Graph Visualization

## Design

The `ExecutionGraphView` is designed to support panning and zooming using SwiftUI's `ScrollView`, `Gesture`, and `.scaleEffect` modifiers. It acts as a viewport into the sequence of execution nodes and dependencies.

## Implementation Status

Because the frozen GUI-002 API strictly limits the backend payload to `CompilerInspection` and does not provide node-level graph definitions, the view currently displays a static placeholder sequence (Input Node -> Processing Node -> Output Node) alongside a disclaimer about the API limitations. The interaction logic (zoom, pan, reset) is fully functional and ready to be populated when the backend API supports exposing the `ExecutionGraph`.
