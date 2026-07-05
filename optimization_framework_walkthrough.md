# Optimization Framework Walkthrough

## Introduction
The oMLX Optimization Framework allows for isolated, stateless, and thread-safe compiler optimizations.

## Core Components
1. **Passes** (`omlx/optimization/passes.py`): Base classes `AnalysisPass` and `OptimizationPass`.
2. **Manager** (`omlx/optimization/manager.py`): Registers passes and resolves execution order using topological sorting.
3. **Pipeline** (`omlx/optimization/pipeline.py`): Executes passes on a compiler artifact.
4. **Validation** (`omlx/optimization/validation.py`): Validates pass dependencies and compatibility.
5. **Diagnostics & Stats** (`omlx/optimization/diagnostics.py`, `omlx/optimization/statistics.py`): Tracks execution details.

## How to use
Instantiate a `PassManager`, register passes, instantiate an `OptimizationPipeline` with the manager and desired stage, and call `.execute(artifact, context)`.
