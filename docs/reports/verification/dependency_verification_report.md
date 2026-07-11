# Dependency Verification Report

- Runtime depends on Compiler components.
- Compiler components depend on Backend Adapter interfaces.
- Backend Adapters depend on specific execution details.
- No reverse dependencies exist. `LoweringEngine` has no knowledge of `Runtime`. The compiler has no knowledge of the legacy `BatchedEngine`.
