# Queue Framework Guide
The Queue Framework establishes an independent orchestration subsystem for managing request admission and lifecycle before execution in OMLX.

## Architecture
- **Queue**: Owns request admission, ordering, and pre-execution lifecycle via `QueueSession`.
- **Runtime**: Owns execution via `RuntimeSession`.
- **Immutable Artifacts**: `QueueDescriptor`, `QueueEntry`, `QueueSession`, `QueueStatistics`, `QueueDiagnostics`.

## Key Components
- `QueueAdmissionController`: Admits requests and generates `QueueEntry`.
- `QueueManager`: Manages the queue lifecycle (enqueue/dequeue) and ordering in a thread-safe manner.
- `QueueAPI`: Exposes passive read-only queue diagnostics.
