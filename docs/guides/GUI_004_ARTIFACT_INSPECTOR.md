# GUI-004 Artifact Inspector

## Functionality

The `ArtifactInspectorView` provides metadata readouts for selected items in the Compiler Explorer (such as individual passes or graph nodes). It is designed to act as the "detail" pane showing identifiers, memory usage, and optimization flags.

## Implementation Details

Because the frozen GUI-002 API does not define DTOs for individual artifact introspection, the Inspector currently binds to the root `CompilerInspection` DTO provided by `DiagnosticsServiceProtocol`. It reliably displays `compilerVersion` and `graphStatus`, while correctly identifying the limitation preventing deeper structural introspection.
