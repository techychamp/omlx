# API-003 Public API Audit

## Audit Results

1.  **`omlx.api.v1.runtime`**: Removed internal runtime object exposure. Introduced `RuntimeService` as an opaque facade. `RuntimeBuilder` now returns `RuntimeService`.
2.  **`omlx.api.v1.compiler`**: Removed `ExecutionIR` and other internal graph structures from the public API. Introduced `CompilerService` wrapping the `CompilerEngine`.
3.  **Models**: Updated all request, response, and descriptor models (like `CompilerRequest`, `ModelDescriptor`, etc.) to use `frozen=True` in their Pydantic `BaseModel` definitions, enforcing immutability.
4.  **Services Layer**: Added new cohesion services: `ModelService`, `GenerationService`, `StreamingService`, `ObservationService`, `QuantizationService`, and `CapabilityService`.
5.  **Thread Safety**: Services themselves are stateless, relying on passed immutable request objects and returning immutable response objects.

All exposed classes strictly encapsulate Runtime internals.
