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
