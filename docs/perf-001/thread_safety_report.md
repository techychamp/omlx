# Thread Safety Report

## Approach
1. **Locks**: Standard `threading.RLock()` is used in `CompilerCache` for all mutations.
2. **Diagnostics**: A separate `threading.Lock()` protects the diagnostic aggregations to avoid blocking cache reads/writes heavily.
3. **Immutability**: `CacheEntry` instances are strictly immutable. When a hit count is updated, a new instance is created and swapped, avoiding race conditions during concurrent reads.

## Verification
Thread safety has been tested in `tests/test_compiler_perf.py` via concurrent worker threads executing continuous `.put()` and `.get()` operations, verifying that diagnostics sum perfectly and no data corruption occurs.
