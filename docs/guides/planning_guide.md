# Diffusion Planning Guide

## Overview
The Diffusion Planning Domain provides immutable, compiler-native preparation for diffusion generation execution. It ensures execution intent is securely captured before dispatching to the runtime, preserving strict separation of concerns.

## Artifacts
The domain relies on fully immutable frozen dataclasses located in `omlx/planner/domains/diffusion/artifacts/`:
- `DiffusionDescriptor`: Identifies architecture, denoiser type, latents, and conditioning.
- `TimestepDescriptor`: Captures scheduler metadata and step counts.
- `LatentDescriptor`: Describes latent representation (channels, height, width).
- `ConditioningDescriptor`: Outlines CFG, text, and image conditioning support.
- `DiffusionRequirement`: Request parameters.
- `DiffusionPlan`: The final coordinated execution plan.

## Usage
The `DiffusionPlanner` receives a `DiffusionDescriptor` and `DiffusionRequirement` to deterministically produce a `DiffusionPlan`. This plan is fully stateless and requires no runtime context or tensor execution capabilities.
