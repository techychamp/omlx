# Optimization Pipeline Guide

## Overview
The Optimization Pipeline orchestrates passes applied to the IR graphs.

## Pipeline Structure
- Logical Passes: Apply to `ExecutionIR`. Examples include constant folding and node elimination.
- Physical Passes: Apply to `PhysicalIR`. Examples include device-specific fusion and memory optimizations.

## Registration
Passes are registered in `LogicalPassRegistry` and `PhysicalPassRegistry`. The `CompilerEngine` executes these passes sequentially.
