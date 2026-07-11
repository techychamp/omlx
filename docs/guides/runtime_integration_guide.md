# Runtime Integration Guide

## Runtime Ownership
The Runtime manages the `RuntimeSession`, coordinates execution strategies, and initiates execution via the `ExecutionEngine`.

## Diffusion Integration
The Runtime accepts the `DiffusionPlan` via the `PlanningBundle` and delegates it to the `DiffusionGenerationStrategy`. The Runtime does not understand diffusion internals, denoising semantics, or timestep implementations, ensuring thread-safe operations across sessions.
