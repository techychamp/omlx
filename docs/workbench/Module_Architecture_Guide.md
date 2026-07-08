# Module Architecture Guide

## Overview
The Workbench uses a modular architecture. Each module exposes a subset of data from the OMLX platform.

## Standard Modules
- **DashboardModule**: System-wide summary.
- **RuntimeExplorerModule**: Execution sessions and timeline.
- **CompilerExplorerModule**: Compilation passes and graph info.
- **PlanningExplorerModule**: Planning domains overview.
- **ModelExplorerModule**: Inspect model metadata.
- **DiagnosticsExplorerModule**: Platform health and issues.
- **PluginExplorerModule**: Loaded plugins and their states.
- **SessionExplorerModule**: Detailed tracking of individual sessions.

## Designing New Modules
1. Define the specific public API endpoints needed.
2. Structure the data response in a UI-agnostic dictionary (`get_module_data()`).
3. Maintain statelessness. Do not cache data in the module unless required, rely on the OMLX backend to maintain state.
