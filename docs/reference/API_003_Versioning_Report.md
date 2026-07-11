# API-003 Versioning Report

## Versioning Strategy

-   **Version Boundary**: The API contract defined in `omlx.api.v1` constitutes the stable v1 API.
-   **Immutability Contract**: All v1 models are strictly immutable. Additions will require new fields with default values to maintain backwards compatibility.
-   **Service Contract**: All services provide functional interfaces without exposing mutable state.
-   **Future V2**: Any breaking changes to parameter names, mandatory constraints, or removal of services will require an explicit `omlx.api.v2` namespace.
