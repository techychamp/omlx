# Registry Infrastructure Walkthrough (IMP-003)

## Overview

This document walks through the architectural changes introduced in IMP-003. This checkpoint implements a generic registry framework designed to support all future runtime metadata operations without modifying existing inference or scheduling behaviors.

## Implementation Details

### `GenericRegistry` (omlx/registry/base.py)
A generic, strongly-typed registry system supporting lifecycle phases (`UNINITIALIZED`, `BUILDING`, `LOCKED`, `SHUTDOWN`).
Key features:
- Registration, lookup, and iteration support.
- JSON Serialization (`to_json`, `from_json`).
- Circular dependency checking.
- Validation for missing dependencies or duplicate definitions.
- Thread-safe implementations using an internal `RLock`.

### Specific Registries (omlx/registry/core.py)
Several concrete registries inherit from `GenericRegistry`:
- `MetadataCapabilityRegistry`
- `MetadataExecutionModeRegistry`
- `MetadataExecutionProfileRegistry`
- `MetadataAdapterRegistry`
- `MetadataPluginRegistry`
- `MetadataVerificationRegistry`
- `MetadataBackendRegistry`

These serve strictly as metadata stores (no runtime/execution logic). The `Metadata` prefix ensures we do not shadow existing global classes during this transition phase.

## Future Migration Path
Subsequent checkpoints will replace specific hardcoded registry behaviors:
1. `GenerationStrategyRegistry` in `capability_registry.py` -> `MetadataCapabilityRegistry`
2. `ExecutionProfileRegistry` in `execution_profile.py` -> `MetadataExecutionProfileRegistry`
3. `ModelRegistry` in `model_registry.py` -> TBD based on tracking scope (engine ownership is state, not metadata, but may be reorganized).
4. Runtime injection will bind instances of these new specific registries to the central `RuntimeBuilder` object, ensuring the application acts as the true Composition Root.

## Verification Evidence
- Tested legacy dependencies: Imports such as `ExecutionProfileRegistry` run without modification.
- Evaluated `tests/test_model_registry.py`: Tests continue to pass, ensuring no unintended impacts on engine functionality.
- Created `tests/test_registry.py`: Comprehensive test suite validating locking, registration duplicates, cycle detection, alias usage, and serializations.

## Rollback Procedure
If regressions are spotted:
1. Revert `omlx/registry/__init__.py` to its previous state (discarding `.base` and `.core` exports).
2. Remove `omlx/registry/base.py` and `omlx/registry/core.py`.
3. Legacy mechanisms remain operational and were unmodified throughout this implementation, resulting in a zero-risk rollback operation.

## Recommendations for IMP-004
1. Define the specific metadata structures required for instances of `MetadataExecutionProfileEntry` or `MetadataAdapterEntry`.
2. Connect `RuntimeBuilder` to pre-populate and lock these registries at startup.
3. Establish a standard format for disk-based configuration ingestion directly into these registries (e.g., an `omlx-plugins.json` format).
# IMP-002: RuntimeBuilder & Composition Root

## Architecture Report
- The `RuntimeBuilder` and `Runtime` classes have been implemented in `omlx/runtime/builder.py`.
- The `RuntimeContext` acts as an immutable configuration object.
- The `Runtime` object acts as the Composition Root, owning components like `engine_pool`, `settings`, and `feature_flags`.
- `omlx/server.py` has been updated to initialize the `Runtime` using `RuntimeBuilder` during `init_server()`, and `_server_state` now delegates `engine_pool` access to the runtime object if present.

## Verification Report
- The tests for `RuntimeBuilder` have been executed and passed.
- No execution logic or models have been altered.
- All legacy behavior is preserved using `_server_state` delegation.

## Rollback Procedure
To rollback, simply revert `omlx/server.py` to remove the `RuntimeBuilder` instantiation in `init_server()` and `get_engine_pool()`, and delete `omlx/runtime/builder.py`.

## Recommendations for IMP-003
- Proceed with migrating `ExecutionPlanner` and `ModelAdapters` to be owned by the `Runtime`.
- Start removing direct usages of `_server_state` across the repository in favor of dependency injection via API routes (e.g. `FastAPI Depends()`).
# Feature Flag Infrastructure Walkthrough (IMP-001)

This walkthrough documents the design and implementation of the Feature Flag Infrastructure for the oMLX repository, satisfying the requirements of IMP-001.

## Architecture

The Feature Flag subsystem is a foundational, zero-dependency architectural component designed to orchestrate safe migrations and code rollout in oMLX without muddying the core execution logic.

The system is strictly divided into three concerns:
1. **Definition (`models.py`)**: Strongly-typed `FeatureFlag` representations powered by `pydantic`.
2. **Registration & Resolution (`registry.py`, `resolver.py`)**: Responsible for gathering flags, storing them before boot, and resolving their values via a deterministic precedence hierarchy.
3. **Immutability & Access (`system.py`)**: Provides a runtime snapshot mechanism. After `take_snapshot()` is called during the `RuntimeBuilder` bootstrap phase, the registry is sealed, and components are provided an `ImmutableSnapshot` guaranteeing no flag changes mid-execution.

## Key Features

- **Strict Lifecycles**: All flags must explicitly declare their lifecycle stage (Shadow -> Experimental -> Dual Run -> Validation -> Primary -> Deprecated -> Removed).
- **Categorization**: Flags are categorized into domains (Runtime, Execution, Planner, Adapter, etc.) to aid in observability.
- **Precedence Hierarchy**:
  1. CLI overrides
  2. Environment Variables
  3. Configuration File
  4. Hardcoded Defaults
- **Thread-Safety via Immutability**: There are no global mutable dictionaries during execution. The snapshot pattern guarantees lock-free, deterministic behavior for the scheduler and execution threads.

## Precedence and Resolution

The `FeatureFlagResolver` determines the value of a flag using the precedence rules. By default, it derives the environment variable name programmatically (e.g., `my-flag` becomes `OMLX_FF_MY_FLAG`) but supports explicit `env_var_name` overrides in the `FeatureFlag` definition.

## Rollback Procedure

Because this PR only introduces infrastructure and changes no runtime behavior, rolling back is purely dropping the `omlx/feature_flags` directory. None of the existing features depend on it yet.

## Recommendations for IMP-002 (RuntimeBuilder)

1. The `RuntimeBuilder` should initialize the `feature_flags_system` during the **BOOTSTRAP** phase.
2. It should populate any CLI overrides or configuration file overrides before taking the snapshot.
3. It must call `feature_flags_system.take_snapshot()` to lock the flags, and then pass the `ImmutableSnapshot` into the dependency injection container for other components (like `Scheduler`, `ExecutionPlanner`) to consume.
