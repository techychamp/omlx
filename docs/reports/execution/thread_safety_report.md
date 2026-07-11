# Thread Safety Report

## Assessment
The backend selection logic was reviewed for thread safety. In an async engine, multiple requests or background tasks might query registries concurrently.

## Registries
`AdapterRegistry` uses `threading.RLock()` to guarantee that `register()`, `resolve()`, and `query()` do not step on each other.

## Data Structures
All configuration and diagnostic data structures introduced in `selection/` are strictly immutable:
- They use `@dataclass(frozen=True)`.
- Dictionaries are wrapped in `MappingProxyType`.
- Lists are converted to `tuple`.

## Conclusion
Parallel backend evaluation, registry lookups, and capability checking can safely occur across multiple threads without risking data races.
