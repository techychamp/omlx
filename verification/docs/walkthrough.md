# Verification Framework Walkthrough

This document serves as an end-to-end walkthrough for the oMLX Verification Framework.
The Verification Framework is designed to prevent regressions and validate the runtime correctness, compiler correctness, backend alignment, and migration accuracy.

## Stages of Verification
1. **Golden Verification**: Ensures the framework adheres exactly to known 'golden' answers (e.g. outputs, tensors, latency constraints).
2. **Runtime Equivalence Testing**: Confirms the legacy runtime behaves identically to the new compiler runtime.
3. **Compiler Verification**: Checks every phase of the compiler pipeline independently (Logical IR -> Lowering -> Physical IR).
4. **Backend Verification**: Validates the translation correctness of the backend graph before execution.
5. **Regression & Stress Infrastructure**: Reusable fixtures and setups for running continuous regressions and load-testing concurrent paths.
6. **Thread Safety**: Detects race conditions.

By strictly following these verification steps in continuous testing, we preserve repository correctness against future changes.
