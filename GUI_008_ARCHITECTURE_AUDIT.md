# GUI-008 Architecture Audit

## Adherence to View -> ViewModel -> Service Layer
The overarching architecture laid down in `GUI_002_API_FREEZE.md` dictates that no SwiftUI `View` or `ViewModel` should ever instantiate backend networking or services independently.

- **Workspace (GUI-003):** Verified.
- **Compiler Explorer (GUI-004):** Verified. Uses `DiagnosticsService` via `AppServices`.
- **Model Management & Admin (GUI-005):** Verified.
- **Diagnostics (GUI-006):** Verified.
- **Developer Studio (GUI-007):** Verified.
- **Legacy Settings (GUI-001/002):** Although legacy settings exist, the newer architectural patterns were prioritized for any new workspaces.

All active GUI modules strictly extract dependencies through `@Environment(AppServices.self)`. `OMLXClient` instantiation is securely restricted within `AppServices`. No violations were found in the current feature branches.
