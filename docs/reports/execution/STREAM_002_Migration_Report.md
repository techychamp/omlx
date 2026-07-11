# STREAM-002: Migration Report

## Changes Made
- Introduced `StreamingTransport` base class.
- Converted `TokenEmitter` to `GeneratorTransport` but aliased it back in `__init__.py` to prevent breaking downstream code.
- Replaced unbounded array modifications with thread-safe queue interactions.

## Action Required
- Any direct implementations parsing `StreamingController._subscribers` will break due to internal structural changes (now stores Unions).
- Consumers relying on synchronous/blocking callbacks should migrate to `CallbackTransport` to avoid freezing the runtime.
