# Golden Testing Guide

Golden tests assert that core components behave deterministically and match reference assets exactly.

## What is a Golden Asset?
A Golden Asset is a serialized snapshot of an expected outcome. In the oMLX framework, golden tests verify:
- CapabilityDescriptors
- ExecutionPlans
- Logical IR & Physical IR
- Backend Operation Graphs
- Compiler diagnostics & Translation diagnostics
- Validation results

## Versioning Golden Assets
All Golden assets must be versioned. Store assets inside `verification/goldens/v{VERSION}/`.
When bumping an API or behavior that requires a change to a golden asset, the asset version must be incremented and an ADR filed.

## Using Utilities
Use the `ArtifactSerializer` from `verification.scripts.utils` to generate JSON payloads. Compare objects in tests using `GoldenComparator.compare()`. It produces deep structural diffs exposing `.added`, `.removed`, and `.changed` dictionary keys without string matching.
