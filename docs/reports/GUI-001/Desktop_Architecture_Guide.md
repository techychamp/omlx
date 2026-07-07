# Desktop Architecture Guide

## Core Principles
1. **API as Boundary:** The Swift UI communicates entirely through the public `omlx` server API. It never imports Python frameworks directly.
2. **SwiftUI Shell:** The app acts as a visual wrapper for configuration, status monitoring, and launching Workbench instances.
3. **App Services Container:** Dependency injection makes networking, file system interaction, and window launching modular and testable.

## Components
- `AppDelegate` / `oMLXApp.swift`: App lifecycle and root view instantiation.
- `MenubarController`: Native top-bar status indicators.
- `AppView`: Master-detail view grouping sections (Settings, Log, Benchmark).
