# Thread Safety Report

The Optimization Framework ensures thread safety by:
1. **Stateless Passes**: Passes are instantiated once but must not retain state between `.apply()` calls.
2. **Context Isolation**: Each pipeline execution receives a unique `OptimizationContext`.
3. **Immutable Artifacts**: Optimization passes return *new* artifacts rather than mutating them in place (where applicable to the artifact type).
