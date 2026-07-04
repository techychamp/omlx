# Future Runtime Integration Notes

- The `CacheManager` should be instantiated inside `RuntimeBuilder` and passed down as a dependency to the `ExecutionPlanner`.
- Diagnostics can be wired to the existing `/metrics` HTTP endpoints.
- Feature flags (`OMLX_FF_COMPILER_CACHE`) should control whether caches are bypassed.
