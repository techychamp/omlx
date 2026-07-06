# Fusion Ownership Report

- **Fusion Planning**: Owns fusion discovery (`FusionAnalyzer`), validation (`FusionValidator`), compatibility, grouping, and emits immutable descriptors (`FusionPlan`).
- **Graph Framework**: Owns graph representation.
- **Graph Analysis**: Owns graph inspection. Fusion Planning consumes Graph Analysis.
- **Compiler**: Owns `FusionPlan` generation and refines execution.
- **Runtime**: Owns execution lifecycle.
- **Scheduler**: Owns dependency ordering.
- **ExecutionEngine**: Owns execution.
- **Backend**: Owns backend execution.
