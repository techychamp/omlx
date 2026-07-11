# GUI-004 Compiler Explorer Workspace

## Architecture

The Compiler Explorer implements a read-only visualizer for the oMLX compiler pipeline and execution artifacts. It leverages the MVVM pattern with `CompilerViewModel` interacting with the backend exclusively through `DiagnosticsServiceProtocol`.

## API Constraints & Limitations

In strict adherence to `GUI_002_API_FREEZE.md`, no new network calls, endpoints, or DTOs have been introduced. The v1 compiler endpoints available via `DiagnosticsServiceProtocol` currently expose limited information, consisting primarily of `CompilerInspection` (containing `compilerVersion` and `graphStatus`).

As a result:
* The **Planning Explorer** shows the overall compiler status rather than the full `PlanningBundle`.
* The **Execution Graph**, **Optimization Reports**, and **Timeline** views display static architectural limitations gracefully, as the granular graph structure and profiling reports are not exposed in the frozen v1 DTOs.
* The workspace remains entirely read-only.
