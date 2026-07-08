# GUI-002: API Freeze & Service Layer Architecture

This document finalizes the production GUI communication architecture for OMLX. It establishes the canonical API contract, MVVM service architecture, dependency injection rules, and streaming infrastructure that every subsequent GUI milestone (GUI-003 through GUI-008) must consume.

## 1. Architectural Invariants

The following ownership model is mandatory across the macOS SwiftUI app:

```text
SwiftUI Views
        │
        ▼
ViewModels (MVVM)
        │
        ▼
Application Services (Protocol-based)
        │
        ▼
OMLXClient (Transport Layer)
```

**Rules:**
1. **No direct networking in ViewModels**: ViewModels must never invoke `OMLXClient`, `URLSession`, or any HTTP request directly. They must use injected Service protocols.
2. **Immutable Data Transfer Objects (DTOs)**: Services must return strictly typed, immutable DTOs (e.g., `GenerateResponse`, `RuntimeStatus`). Raw JSON dictionaries must not escape the networking boundary.
3. **Transport Agnosticism**: Services must not assume the runtime is local. The `OMLXClient` acts as the sole boundary between the app and the backend.

## 2. API Compatibility Rules

The following rules govern the evolution of the frozen `v1` API surface:

1. **Additive Only**: Public `v1` endpoints are additive only.
2. **Immutable Fields**: Existing DTO fields cannot be renamed or removed within the `v1` lifecycle.
3. **Optional Additions**: New fields introduced in `v1` must be optional unless a new `apiVersion` is introduced.
4. **Breaking Changes**: Any breaking change requires a new API version (e.g., `v2`).

## 3. Streaming Abstraction

All streaming endpoints must use the canonical `AsyncThrowingStream<T, Error>` abstraction provided by `OMLXClient.stream<T>()`.
This unified parser handles Server-Sent Events (SSE) generic over any `Decodable` type, ensuring a consistent interface for text generation, compiler progress, and event streams.

Example:
```swift
func stream(request: GenerateRequest) -> AsyncThrowingStream<GenerationChunk, Error>
```

## 4. Frozen v1 API Surface

The API surface is now frozen with the following domain routes:

- `/v1/chat/completions` — Core generation and streaming.
- `/v1/models` — Model discovery, loading, and unloading.
- `/v1/runtime` — System status, backend info, and capabilities.
- `/v1/sessions` — Chat session persistence and state.
- `/v1/compiler` — Graph compilation progress and inspection.
- `/v1/diagnostics` — Telemetry (execution, Apple Silicon metrics).
- `/v1/benchmarks` — Standardized benchmarking operations.

## 5. Mocking Strategy

To support rapid iteration and isolated testing, services are mocked at two levels:

1. **Preview Mocks (`Sources/Services/Previews/`)**: Lightweight, hardcoded responses used exclusively for SwiftUI Previews.
2. **Test Mocks (`Tests/oMLXTests/Mocks/`)**: Comprehensive, stateful implementations used for unit and integration testing.

## 6. Service Protocols

The service layer is composed of the following injected dependencies:

- **GenerationService**: Handles chat generation and SSE streaming.
- **PlatformService**: Exposes runtime metadata (version, backend, capabilities).
- **SessionService**: Manages session state and history retrieval.
- **ModelManagementService**: Coordinates model loading and unloading.
- **DiagnosticsService**: Consumes execution, compiler, and hardware telemetry.
