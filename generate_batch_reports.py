def generate():
    reports = {
        "Ownership_Verification_Report.md": """
# Ownership Verification Report

## Batch Realization
- **Compiler**: Verified to be the sole owner of batch realization (`BatchRealizer`).
- **Runtime**: Verified to not perform any batch realization. It only attaches the `BatchExecutionGraph` and `BatchRealizationReport` to the `RuntimeSession`.
- **Queue**: Verified to remain strictly queue-based. No batch grouping or batch graph generation logic exists inside `QueueManager`.
- **Scheduler**: Verified to remain deterministic. It executes the finalized schedule without dynamic or adaptive batch grouping logic.
- **Backend**: Remains entirely oblivious to batch configurations.
""",
        "Compiler_Integration_Report.md": """
# Compiler Integration Report

## Integration of Batch Realization
The batch realization domain has been successfully integrated into the oMLX Compiler.
- Added `omlx/planner/compiler/batch/artifacts.py` containing immutable structures.
- Added `omlx/planner/compiler/batch/realizer.py` for deterministic graph realization.
- Updated `omlx/planner/compiler/compiler.py` to expose `realize_batch`.

The compiler receives a `BatchPlan` and transforms it deterministically into a `BatchExecutionGraph`.
""",
        "Future_Continuous_Batching_Report.md": """
# Future Continuous Batching Report

## Architectural Readiness
By establishing strict compiler-native batch realization boundaries in BATCH-002, the platform is fundamentally prepared for continuous batching (BATCH-003).
Because the Runtime and Execution Engine are explicitly forbidden from mutating batch boundaries dynamically, continuous batching will be achieved via new, discrete compilation artifacts (e.g., streaming batch graphs) rather than unstructured runtime queue merging.
""",
        "Batch_Realization_Guide.md": """
# Batch Realization Guide

## Process Overview
1. A request queue generates a `BatchPlan` via the Batch Planner.
2. The `BatchPlan` is passed to the Compiler.
3. The Compiler's `BatchRealizer` generates a `BatchExecutionGraph`.
4. The `BatchExecutionGraph` is attached to a `RuntimeSession`.
5. The Execution Engine consumes the `BatchExecutionGraph`.
""",
        "Batch_Execution_Guide.md": """
# Batch Execution Guide

## Execution Context
Batch execution is handled deterministically. The Execution Engine does not know the origins of a batch; it simply processes the `BatchExecutionGraph`. The operations within the graph include synchronization and grouping metadata designed by the Compiler.
""",
        "Synchronization_Guide.md": """
# Synchronization Guide

## Synchronization Nodes
Synchronization in batch processing is realized explicitly within the `BatchSynchronizationGraph` as dedicated synchronization nodes. The Execution Engine must respect these barriers but does not generate them.
""",
        "Compiler_Integration_Guide.md": """
# Compiler Integration Guide

## Batch Integration
The compiler manages batching through the `BatchRealizer`. This component translates abstract batch plans into physical graph representations.
""",
        "Architecture_Decision_Record_BATCH002.md": """
# Architecture Decision Record: BATCH-002

## Decision
All batch realization (grouping, synchronization, graph generation) must happen strictly within the Compiler.

## Justification
Keeping the Runtime and Execution Engine free of batching logic ensures they remain deterministic, predictable, and simple. Adapting batching logic as a runtime queue-merging exercise creates non-deterministic execution behavior and hides latency bottlenecks.
""",
        "Migration_Report_BATCH002.md": """
# Migration Report: BATCH-002

## Migration Status
- Migration of batch structures into the compiler is complete.
- No legacy runtime batching routines existed; this was a purely additive feature to the compiler.
"""
    }

    for filename, content in reports.items():
        with open(filename, "w") as f:
            f.write(content.strip() + "\n")

generate()
