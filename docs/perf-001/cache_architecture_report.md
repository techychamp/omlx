# Compiler Cache Architecture Report

## Overview
The compiler cache subsystem provides a layered, thread-safe, and highly configurable caching mechanism for the compiler pipeline. It strictly adheres to the constraint of avoiding runtime integration while providing robust infrastructure.

## Layers
1. **CapabilityCache**: Caches `CapabilityDescriptor` generation.
2. **PlanCache**: Caches `ExecutionPlan` generation.
3. **LogicalIRCache**: Caches Logical IR graphs.
4. **PhysicalIRCache**: Caches lowered Physical IR graphs.
5. **BackendGraphCache**: Caches final backend translations.

## Components
- **CompilerCache**: Base class enforcing thread safety (`threading.RLock`) and managing eviction.
- **CacheManager**: Orchestrates instances of all cache layers and aggregates diagnostics.
- **CacheKey**: Generates deterministic, immutable hashes based on inputs.
- **CacheEntry**: Immutable dataclass containing cached objects and metadata.
- **EvictionPolicy**: Pluggable strategies (LRU, LFU, FIFO, TTL).
- **CacheDiagnostics**: Thread-safe tracker for hits, misses, evictions, and stage latencies.

## Thread Safety
All state mutations inside the caches and diagnostics are protected by locks, allowing safe concurrent reads and writes from multiple threads (e.g., Engine Thread).
