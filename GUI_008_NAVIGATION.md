# GUI-008 Navigation Architecture

## Overview
oMLX uses `AppView` backed by `AppSection` for top-level navigation, presented via `NavigationSplitView`.

## Routes
- **Workspace:** Main Chat / Execution
- **Compiler Explorer:** Optimization pipeline and execution graph
- **Diagnostics:** Performance telemetry
- **Developer Studio:** API and Trace explorer
- **Runtime Administration:** Session management and configuration
- **Model Management:** Local and remote model catalogs

Cross-workspace links successfully dispatch via `windowStateManager.navigate(to:)` ensuring seamless intra-app flows without orphaned routes.
