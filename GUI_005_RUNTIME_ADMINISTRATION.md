# GUI-005 Runtime Administration Workspace

## Overview

The Runtime Administration workspace (`RuntimeAdministrationView`) provides a lightweight, administrative dashboard detailing the system's current runtime configuration and capabilities.

## Architecture

```text
RuntimeAdministrationView
    ↓
PlatformViewModel (Aggregates metadata)
    ↓
PlatformServiceProtocol & SessionServiceProtocol
    ↓
OMLXClient
```

## Scope & Module Boundaries

The primary goal of GUI-005 is answering the question: *"How is my Runtime configured?"*

It explicitly avoids answering: *"How is my Runtime performing?"* which is the domain of GUI-006 (Diagnostics). Therefore, `RuntimeAdministrationView` aggregates existing immutable Runtime metadata (like server backend, host/port, API versions, and running sessions count), but does **not** duplicate graphs, apple metrics, or execution metrics.

## Cross-Linking

To ensure cohesion without duplicating logic, `RuntimeAdministrationView` provides explicit cross-links (`NavigationLink` or actions mapping to `AppSection` changes) to:
- **Diagnostics** (`GUI-006`)
- **Developer Studio** (`GUI-007`)
- **Compiler Explorer** (`GUI-004`)

This seamlessly hands off users to the appropriate tools when they need to drill down into metrics or lower-level configuration.
