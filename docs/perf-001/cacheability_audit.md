# Cacheability Audit

## Compiler Pipeline Analysis

1. **CapabilityResolver**
   - **Outputs**: `CapabilityDescriptor`
   - **Deterministic**: Yes, given the same `ModelDescriptor` and environment variables.
   - **Cacheable**: Yes.
   - **Immutable**: Yes, `CapabilityDescriptor` is strictly immutable (using tuples, frozensets, MappingProxyType).

2. **ExecutionPlanner**
   - **Outputs**: `ExecutionPlan`
   - **Deterministic**: Yes, given the same `CapabilityDescriptor` and planner version/plugins.
   - **Cacheable**: Yes.
   - **Immutable**: Yes, `ExecutionPlan` is an immutable dataclass.

3. **Logical IR Generation**
   - **Outputs**: Logical IR Graph
   - **Deterministic**: Yes, given the same `ExecutionPlan`.
   - **Cacheable**: Yes.
   - **Immutable**: Yes.

4. **Physical IR Lowering**
   - **Outputs**: Physical IR Graph
   - **Deterministic**: Yes, given the same Logical IR.
   - **Cacheable**: Yes.
   - **Immutable**: Yes.

5. **Backend Translation**
   - **Outputs**: BackendOperationGraph
   - **Deterministic**: Yes, given the same Physical IR and Backend Adapter version.
   - **Cacheable**: Yes.
   - **Immutable**: Yes.

## Required Cache Keys
To ensure reproducible and correct caching without collisions, the following inputs must be part of the deterministic cache key generation:
- Model Identifier
- Model Version
- Execution Family
- Execution Mode
- Feature Flags Snapshot
- Backend ID
- Adapter Version
- Compiler Version
- Planner Version
- Capability Hash
- Execution Hints

All cache keys must avoid object identity and rely strictly on reproducible hashing of immutable values.

## Conclusion
The compiler pipeline follows a strictly immutable and deterministic design, making it a perfect candidate for multi-layered caching. Since none of the steps rely on runtime globals or mutable state during planning, caching can be safely implemented at each layer.
