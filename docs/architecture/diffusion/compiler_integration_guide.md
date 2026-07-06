# Compiler Integration Guide

## Compiler Ownership
The Compiler acts as the central orchestrator for planning, utilizing the `CompilerPlanner` to assemble the `PlanningBundle`.

## Diffusion Integration
The Compiler natively invokes the `DiffusionPlanner` if required. The resulting `DiffusionPlan` is attached immutably to the `PlanningBundle`.
The Compiler **never** executes diffusion or performs denoising, guaranteeing a purely metadata-driven, graph-producing pipeline.
