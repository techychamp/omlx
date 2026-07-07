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
