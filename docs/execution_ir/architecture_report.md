# Execution IR Architecture Report

## Overview
Execution IR is the canonical logical representation of an execution pipeline. It represents execution as an immutable, directed acyclic graph (DAG). The goal is to separate execution planning from backend execution entirely.

## Architecture
The architectural flow is now:
1. `CapabilityDescriptor`
2. `ExecutionPlanner`
3. `ExecutionPlan`
4. `IRBuilder` (owned by `Runtime`)
5. `ExecutionIR` (DAG of `IRNode`s)
6. `ExecutionBackend` (Future integration)

## Decisions
- Execution IR is fully immutable and stateless to ensure thread safety during planning.
- The IR does NOT contain any actual MLX operations, runtime allocations, or model states.
- Replaced linear sequences with a dependency-based DAG.

## Audit Impact
Existing `ExecutionBackend` components (e.g. `autoregressive_backend`, `experimental_diffusion_backend`) contain hardcoded execution sequences. Introducing ExecutionIR will decouple this, allowing these backends to receive an IR graph to execute dynamically.
