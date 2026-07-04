# Compiler Performance Audit

## Overview
This document outlines the performance audit of the compiler pipeline, identifying areas for caching, reuse, and incremental compilation.

## Recomputed Stages
- Capability Resolution (CapabilityResolver)
- Execution Planning (ExecutionPlanner)
- Logical IR Generation (IRBuilder)
- Lowering to Physical IR (LoweringEngine)
- Backend Translation (BaseBackendAdapter)

## Immutable Objects
- `CapabilityDescriptor`
- `ExecutionPlan`
- `ExecutionIR`
- `PhysicalIR`
- `TranslationResult`
- `BackendOperationGraph`

## Reusable Compiler Outputs
- Capability resolution results can be reused if the descriptor hasn't changed.
- Execution plans can be reused for identical capability descriptors.
- Logical and Physical IRs can be cached and reused across identical execution plans.

## Deterministic Computations
All compiler stages listed above are deterministic and do not depend on runtime state.

## Cache Strategies
We implemented a hierarchical cache with thread-safe LRU eviction and memory bounding:
- `CapabilityDescriptor` (small)
- `ExecutionPlan` (medium)
- `ExecutionIR` (medium)
- `PhysicalIR` (large)
- `TranslationResult` (large)
