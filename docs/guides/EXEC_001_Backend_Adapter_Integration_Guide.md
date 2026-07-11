# Backend Adapter Integration Guide

Execution Engine delegates final execution to `BackendAdapter` classes.

## Compatibility
`EXEC-001` focuses purely on ownership transition. Backend adapters have not been rewritten; they maintain their current APIs, producing `BackendOperationGraph`s. The dispatcher iterates over these graphs.
