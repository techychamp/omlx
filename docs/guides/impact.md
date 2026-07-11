# Repository Impact Report
No runtime behavior was altered. The `TranslationResult` now produces cost estimates. `BackendDescriptor` is larger but remains compatible with existing descriptor initializations due to default arguments. The new intelligence framework is completely isolated in `omlx/planner/compiler/backend/intelligence`.
