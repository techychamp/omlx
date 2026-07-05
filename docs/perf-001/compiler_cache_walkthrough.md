# Compiler Cache Walkthrough

## How it works

1. **Initialization**: The system initializes a `CacheManager` with desired capacity constraints for each layer.
2. **Key Generation**: Before executing a compiler stage, a `CacheKey` is generated using deterministic inputs (e.g., model ID, feature flags).
3. **Lookup**: The corresponding cache layer is queried.
    - If a **hit** occurs, the `CacheEntry` is duplicated with an updated `hit_count`, the eviction policy updates its state, diagnostics record the hit, and the cached object is returned.
    - If a **miss** occurs, execution proceeds normally.
4. **Storage**: After generating the output, the compiler injects it into the cache layer using `.put()`.
5. **Eviction**: If capacity is exceeded during `.put()`, the configured `EvictionPolicy` selects a key to remove, and it is cleanly deleted.
