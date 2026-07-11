# Dead Code Analysis & Subsystem Status Report

A complete repository audit identified and dispositioned dead or disconnected subsystems:

## 1. Duplicate Optimization Framework
* **Path:** `omlx/planner/compiler/optimization_pipeline.py`
* **Status:** **Removed**
* **Reason:** Replaced entirely by the canonical, topology-aware `omlx/optimization/pipeline.py`.

## 2. Duplicate PlanningBundle
* **Path:** `omlx/planner/bundle.py`
* **Status:** **Removed**
* **Reason:** Functionality merged into the canonical `omlx/planner/domains/bundle.py`.

## 3. Optimization Intelligence Subsystem
* **Path:** `omlx/optimization/intelligence/`
* **Status:** **Integrated**
* **Reason:** `OptimizationPlanner` (and its dependencies `CostCache`, `AdaptiveOptimizationPolicy`, `IntelligenceStatisticsTracker`) is now instantiated natively within `CompilerEngine` to filter passes dynamically across all CompilerStages.

## 4. Apple Silicon Optimization Subsystem
* **Path:** `omlx/optimization/apple/`
* **Status:** **Integrated**
* **Reason:** `AppleDeviceOptimizationPass` is now formally registered to a `CompilerStage.EXECUTION_PLAN` pass manager and evaluated natively in the compiler execution flow before Logical IR generation.
