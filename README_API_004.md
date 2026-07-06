# API-004 SDK Implementation

The API-004 milestone has been successfully implemented by introducing a production-quality client interface over the existing Runtime.

## What was implemented

### OMLXClient
A first-class SDK client object (`omlx.api.v1.client.OMLXClient`) serves as the main entry point, providing a simplified facade while rigorously respecting the rule of *not containing any execution logic itself*. It safely delegates to `RuntimeService`.

### Session Management
Immutable `SessionDescriptor` objects manage explicit user sessions without polluting the underlying internal engine states.

### Configuration Profiles
Profiles can be defined and reused easily by registering `RuntimeConfig` structures.

### Thread Safety & Isolation
No mutable global states are used, permitting multiple clients and sessions simultaneously.
Errors are strictly mapped to an extended unified `omlx.api.v1.exceptions` hierarchy (with new typed `RuntimeError`).

## Testing
`test_api_v1_client.py` has been provided which tests session lifecycle, synchronous and asynchronous generation APIs, exception translation, and configuration profile management.
