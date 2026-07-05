# Incremental Compilation Walkthrough

## Overview
Incremental compilation allows us to avoid recompiling downstream artifacts if upstream ones haven't changed.

## Implementation
We implemented a `DependencyTracker` which maintains a Directed Acyclic Graph (DAG) of cache keys.

Example flow:
1. `CapabilityResolver` cache miss -> creates `cap_desc_xxx`.
2. `ExecutionPlanner` cache miss -> creates `plan_xxx`. Tracker records `cap_desc_xxx` -> `plan_xxx`.
3. `IRBuilder` cache miss -> creates `ir_xxx`. Tracker records `plan_xxx` -> `ir_xxx`.

If the capability descriptor cache hit occurs, we can immediately return the cached artifact, saving the downstream steps if they also hit. If an upstream artifact is invalidated, the `DependencyTracker` can be queried to invalidate all transitive downstream artifacts.
