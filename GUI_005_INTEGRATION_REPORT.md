# GUI-005 Integration Report

## Module Ownership & Boundary Adherence

During the implementation of GUI-005, explicit care was taken to respect the boundaries established by GUI-006 (Diagnostics).

### Why Runtime Health was Not Duplicated
A proposed `RuntimeHealthView` was intentionally excluded from GUI-005 because performance profiling, execution metrics, and hardware telemetry (Apple Silicon metrics) are fully owned by GUI-006. Re-implementing a "health" dashboard within Runtime Administration would violate the separation of concerns and duplicate complex presentation logic. Instead, GUI-005 provides a strictly administrative `RuntimeOverviewCard` summarizing the immutable configuration, and delegates health monitoring to Diagnostics via cross-workspace navigation links.

### Cross-Linking Logic
To maintain app cohesion without duplicating functionality, `RuntimeAdministrationView` includes explicit `NavigationLink`-style buttons to jump into:
- **Diagnostics** (GUI-006) for runtime health and performance metrics.
- **Developer Studio** (GUI-007) and **Compiler Explorer** (GUI-004) for deeper runtime introspection.

These links set `services.requestedSection` to route the user within the `AppView` shell seamlessly.

## API Freeze Compliance

GUI-005 adheres strictly to the `GUI_002_API_FREEZE.md` specification:
1. **No New DTOs**: Only existing structs (`ModelInfo`, `RuntimeStatus`, `ServerInfo`, `CapabilityReport`, `SessionInfo`) were consumed.
2. **No Fabricated Data**: Properties not exposed by the current `v1` API (e.g. model context lengths, parameters, or quantization formats) are not guessed, derived, or mocked in production code. The UI explicitly renders *"Unavailable via current Runtime API"* for these fields.
3. **No Unsupported Mutations**: Because the `v1` API does not yet define endpoints to rename, delete, or merge chat sessions, or endpoints to delete and download models, the Views explicitly label these interactions as unavailable rather than introducing mock business logic.

This design ensures the codebase remains aligned with the established backend contracts and minimizes breaking changes when the `v2` API is introduced.
