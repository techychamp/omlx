# Architecture Decision Record: Developer Workbench

## Context
With the maturity of the compiler and runtime foundations, a unified interface is required to observe and inspect the platform's state (WORKBENCH-001).

## Decision
We implemented a `DeveloperWorkbench` layer located in `omlx/workbench`. This layer is strictly a client of the public `omlx.api.v1` APIs.

## Rationale
- **Separation of Concerns:** Execution and compilation remain isolated from the presentation layer.
- **Modularity:** Using `NavigationManager`, new visual modules can be added dynamically, anticipating future GUI capabilities.
- **Safety:** By strictly consuming public APIs, we ensure the Workbench cannot corrupt or bypass the runtime/compiler state.

## Consequences
- The Workbench does not execute models.
- All new data required for the UI must first be exposed via `OMLXClient`.
