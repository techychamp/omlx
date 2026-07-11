# Diffusion Strategy Guide

## Overview
The `DiffusionGenerationStrategy` orchestrates generation. It receives an immutable `DiffusionPlan` from the compiler and handles the execution coordination (e.g. stepping through the timestep schedule).

## Responsibilities
- It owns **only** orchestration.
- It does **not** understand diffusion algorithms, perform denoising, execute tensors, or modify the Runtime ownership boundaries.

## Registration
The strategy is registered within the `GenerationStrategyRegistry` under the key `diffusion`. The `RuntimeBuilder` initializes this strategy contextually based on the execution requirements without exposing any execution specifics to the rest of the backend.
