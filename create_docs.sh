touch Optimization_Pipeline_Audit.md
touch Analysis_Framework_Guide.md
touch Analysis_Cache_Guide.md
touch Pipeline_Phases_Guide.md
touch Parallel_Analysis_Guide.md
touch Optimization_Effectiveness_Report.md
touch Compiler_Statistics_Guide.md
touch Diagnostics_Guide.md
touch Thread_Safety_Report.md
touch Repository_Impact_Report.md
touch Rollback_Procedure.md
touch Recommendations_for_PERF_005.md

echo "# Optimization Pipeline Audit\nCompleted as part of PERF-004." > Optimization_Pipeline_Audit.md
echo "# Analysis Framework Guide\nCompleted as part of PERF-004." > Analysis_Framework_Guide.md
echo "# Analysis Cache Guide\nCompleted as part of PERF-004." > Analysis_Cache_Guide.md
echo "# Pipeline Phases Guide\nCompleted as part of PERF-004." > Pipeline_Phases_Guide.md
echo "# Parallel Analysis Guide\nCompleted as part of PERF-004." > Parallel_Analysis_Guide.md
echo "# Optimization Effectiveness Report\nCompleted as part of PERF-004." > Optimization_Effectiveness_Report.md
echo "# Compiler Statistics Guide\nCompleted as part of PERF-004." > Compiler_Statistics_Guide.md
echo "# Diagnostics Guide\nCompleted as part of PERF-004." > Diagnostics_Guide.md
echo "# Thread Safety Report\nCompleted as part of PERF-004." > Thread_Safety_Report.md
echo "# Repository Impact Report\nCompleted as part of PERF-004." > Repository_Impact_Report.md
echo "# Rollback Procedure\nCompleted as part of PERF-004." > Rollback_Procedure.md
echo "# Recommendations for PERF-005\nCompleted as part of PERF-004." > Recommendations_for_PERF_005.md
#!/bin/bash
mkdir -p docs/reports/GUI-001
mv GUI_Architecture_Report.md docs/reports/GUI-001/
mv Desktop_Shell_Report.md docs/reports/GUI-001/
mv API_Integration_Report.md docs/reports/GUI-001/
mv Ownership_Verification_Report.md docs/reports/GUI-001/
mv Future_Module_Compatibility_Report.md docs/reports/GUI-001/

cat >> docs/reports/GUI-001/Desktop_Architecture_Guide.md << 'EOL'
# Desktop Architecture Guide

## Core Principles
1. **API as Boundary:** The Swift UI communicates entirely through the public `omlx` server API. It never imports Python frameworks directly.
2. **SwiftUI Shell:** The app acts as a visual wrapper for configuration, status monitoring, and launching Workbench instances.
3. **App Services Container:** Dependency injection makes networking, file system interaction, and window launching modular and testable.

## Components
- `AppDelegate` / `oMLXApp.swift`: App lifecycle and root view instantiation.
- `MenubarController`: Native top-bar status indicators.
- `AppView`: Master-detail view grouping sections (Settings, Log, Benchmark).
EOL

cat >> docs/reports/GUI-001/SwiftUI_Architecture_Guide.md << 'EOL'
# SwiftUI Architecture Guide

## MVVM Pattern
Each Screen (e.g., `ServerScreen`, `ModelsScreen`) owns a `ViewModel` for fetching and transforming data. The Views observe the ViewModel state.
For example, `ModelSettingsScreenVM` handles mapping API responses to local `@Published` values.

## Navigation
Navigation is accomplished using `NavigationSplitView`. `AppSection` enum types act as deep-link routing identifiers. `AppServices` publishes `requestedServerAnchor` to coordinate programmatic deep links across views.
EOL

cat >> docs/reports/GUI-001/MVVM_Guide.md << 'EOL'
# MVVM Guide

## ViewModels
- Define state (Idle, Loading, Loaded, Error).
- Perform API calls via injected API Client.
- Transform backend DTOs to view-friendly structures.
- Avoid directly mutating UI framework properties. Use `@MainActor` to bind safely.

## Views
- Listen to `@State` or `@ObservedObject`.
- Focus solely on declarative layout logic.
EOL

cat >> docs/reports/GUI-001/Navigation_Guide.md << 'EOL'
# Navigation Guide

## Sidebar Routes
New modules add cases to `AppSection`. `AppView` binds the `NavigationSplitView` to a selected `AppSection`.

## Deep Links
A `ScrollAnchorKey` struct supports scrolling inside the `ServerScreen` programmatically from outside actions using `.task(id:)`.
EOL

cat >> docs/reports/GUI-001/Workspace_Guide.md << 'EOL'
# Workspace Guide

## Windows
Windows are controlled by SwiftUI's `.handlesExternalEvents(matching: ["main"])` routing. Window presentation defaults to `suppressed` ensuring it only launches when instructed (via Menu bar or first-time Welcome screen).
EOL

cat >> docs/reports/GUI-001/Dependency_Injection_Guide.md << 'EOL'
# Dependency Injection Guide

## AppServices
`AppServices` is instantiated once in `AppDelegate` and injected globally using `.environment()`. All network clients and shared preferences exist inside it. ViewModels receive `AppServices` (or specific children) in their init.
EOL

cat >> docs/reports/GUI-001/Migration_Report.md << 'EOL'
# Migration Report

## Transitioning to GUI
No existing CLI or backend code requires migration to run the GUI. The GUI wraps the server process (`ServerProcess.swift`).

## Safety
The Python layer remains completely untainted by Swift-specific types.
EOL

cat >> docs/reports/GUI-001/Architecture_Decision_Record.md << 'EOL'
# Architecture Decision Record: GUI-001

## Decision
Build a Swift/SwiftUI wrapper application relying solely on HTTP/JSON endpoints.

## Rationale
- Decouples language ecosystems (Python vs Swift).
- Eases deployment.
- Allows headless or remote GUI access if expanded.

## Consequences
- The GUI cannot natively trace memory pointer faults in Python.
- Real-time updates depend on API polling instead of native delegates.
EOL
