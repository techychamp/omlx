# ExecutionPlan Migration Walkthrough

This document explains how the `ExecutionPlan` integrates into the legacy runtime using the compatibility layer.

## Overview

The runtime originally relied on `ExecutionProfileRegistry` and `ExecutionProfile` to determine the execution backend and modes.
In MIG-002, the runtime is being migrated to use the `ExecutionPlanner` which takes a `CapabilityDescriptor` and produces an `ExecutionPlan`.

## The Compatibility Layer

The legacy `Scheduler` and `ExecutionBackend` components still expect an `ExecutionProfile`. To support staged migration, an `ExecutionProfileAdapter` has been created.
- The runtime passes capabilities to the planner to generate an `ExecutionPlan`.
- The plan is then adapted into an `ExecutionProfile` via `ExecutionProfileAdapter`.

## Feature Flags

- `OMLX_FEATURE_EXECUTION_PLAN_RUNTIME`: Enables the planner and adapter route during initialization in `EngineCore`.
- `OMLX_FEATURE_EXECUTION_PROFILE_COMPATIBILITY`: Used to explicitly enable just the compatibility adapter logic (when running alongside the legacy profile generation for testing).
- `OMLX_FEATURE_EXECUTION_PLAN_VALIDATION`: Runs both the legacy `ExecutionProfileRegistry` resolution and the new `ExecutionPlanner` logic, verifying that their outputs match, logging any differences.

## What's Next?
In MIG-003, the `Scheduler` and Backends will be updated to consume `ExecutionPlan` directly, removing the need for `ExecutionProfileAdapter` entirely.
