# GUI Architecture Report

## Overview
The application follows an MVVM architecture using SwiftUI and a Coordinator pattern to manage navigation.
It runs as a macOS menubar application with a main configuration window (`AppView`).

## Dependency Injection
The application uses the `AppServices` object injected into the environment (`.environment(appDelegate.services)`) to manage global state and dependencies like configuration (`AppConfig`) and the network client (`APIClient`).

## Ownership Boundaries
- The GUI shell (SwiftUI) strictly owns windows, layouts, themes, and navigation.
- The Workbench modules are hosted inside the shell.
- The Runtime and Compiler are treated as opaque external services accessed via the API.

## Verification Note
The user requested a "minimal compilable SwiftUI shell". After inspection, `apps/omlx-mac/Sources/` already contains:
- `oMLXApp.swift` (App entry point)
- `AppView/AppView.swift` (Shell with NavigationSplitView)
- `AppView/Screens/ServerScreen.swift` (Dashboard/Settings)
- `AppView/AppServices.swift` (Service Container)
- `Net/OMLXClient.swift` (API Client)

These files already implement the requested application skeleton and compile as part of the `oMLX.xcodeproj` project. The requested implementation work (GUI-001) is confirmed to already exist in the codebase.
