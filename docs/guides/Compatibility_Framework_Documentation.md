# Compatibility Framework Documentation

## Scope
The Compatibility Framework is a sub-system within Backend Selection that produces a boolean `is_compatible` response for a candidate backend, accompanied by string reasons if not compatible.

## Validation Steps
The `CompatibilityChecker.check_compatibility` method evaluates:
1. `BackendDescriptor` constraints (e.g., does it support the requested execution semantics?).
2. Memory model presence.
3. Fallback chain compliance (will generate warnings if out of bounds).

## Output
Returns a `CompatibilityReport`. This output is explicitly consumed by the Selection Framework; if `is_compatible` is False, the backend's score is immediately forced to 0.0.
