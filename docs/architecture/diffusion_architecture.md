# DIFF-001: Compiler-Native Diffusion Execution Strategy & Planning Framework

## Architecture Decision Record

This document outlines the architecture for Diffusion execution within the OMLX runtime.

### Model Intelligence
Diffusion capabilities are extracted via `DiffusionCapabilityExtractor` into a strictly immutable `DiffusionDescriptor`. Models are classified into `Diffusion` families.

### Planning Domain
A new `DiffusionPlanner` generates an immutable `DiffusionPlan`. It evaluates `DiffusionDescriptor` against `DiffusionRequirement` to produce execution metadata, including timestep schedules. The plan is integrated securely into `PlanningBundle`.

### Execution Strategy
`DiffusionGenerationStrategy` orchestrates generation. It receives `DiffusionPlan` and passes actual execution duties to the Runtime Engine, remaining completely agnostic of tensor computations.

### Observability
All diffusion diagnostics and artifacts are generated as strictly immutable outputs like `DiffusionStatistics`. Tooling and observability layers consume these passively.
