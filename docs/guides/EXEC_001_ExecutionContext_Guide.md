# ExecutionContext Guide

`ExecutionContext` is the primary read-only data structure passed into the `ExecutionEngine`.

## Contents
- `backend_operation_graph`: Target execution graph.
- `diagnostics`: Diagnostics created during compilation.
- `statistics`: Pre-computed metrics.
- `request_context`: Original user invocation settings.
