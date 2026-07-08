import os

def create_report(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Generated {filename}")

create_report("GUI_Architecture_Report.md", """# GUI Architecture Report

## Overview
The application follows an MVVM architecture using SwiftUI and a Coordinator pattern to manage navigation.
It runs as a macOS menubar application with a main configuration window (`AppView`).

## Dependency Injection
The application uses the `AppServices` object injected into the environment (`.environment(appDelegate.services)`) to manage global state and dependencies like configuration (`AppConfig`) and the network client (`APIClient`).

## Ownership Boundaries
- The GUI shell (SwiftUI) strictly owns windows, layouts, themes, and navigation.
- The Workbench modules are hosted inside the shell.
- The Runtime and Compiler are treated as opaque external services accessed via the API.
""")

create_report("Desktop_Shell_Report.md", """# Desktop Shell Report

## Window Management
The application starts suppressed without a window (`.defaultLaunchBehavior(.suppressed)`).
It relies on `AppDelegate` to manage the lifecycle of the main window (`NSWindow`) and the Menubar app status.

## Layout & Workspace
The workspace is built using SwiftUI's `NavigationSplitView`.
The sidebar provides access to different sections (e.g., Status, Server, Models) defined in `AppSection`.
""")

create_report("API_Integration_Report.md", """# API Integration Report

## Client
The GUI communicates with the oMLX server using a unified API client architecture (likely located in the `Net` folder, e.g., `APIClient.swift`).

## Polling & Status
`MenubarController` periodically polls the server for status and statistics to keep the UI responsive and accurately reflect the backend state without direct coupling.
""")

create_report("Ownership_Verification_Report.md", """# Ownership Verification Report

## Verification
- **GUI**: Owns presentation layer and native window handles.
- **Runtime**: Not imported directly in the Swift target. Only accessed via local network requests.
- **Compiler**: No direct linkage.
- **API**: Serves as the single boundary for all operations.

Conclusion: Ownership boundaries are preserved.
""")

create_report("Future_Module_Compatibility_Report.md", """# Future Module Compatibility Report

## Extensibility
The `AppSection` enum and `AppView` sidebar implementation allow for dynamic addition of new modules (GUI-002 through GUI-008).
By mapping enum values to new SwiftUI views, the shell can host new features without architectural redesign.

## Next Steps
Future iterations will dynamically populate the sidebar or use plugin manifests if dynamic registration is required.
""")
