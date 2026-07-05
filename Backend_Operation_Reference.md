# Backend Operation Reference

The Backend Operation Graph is composed of standard physical operations that the `MLXAdapter` maps to hardware-specific execution plans.

## Operation Types

### `MLXForwardOperation`
- **Purpose:** Executes the core neural network forward pass.
- **Inputs:** `input_ids`, KV cache state.
- **Outputs:** Model `logits` shape metadata.
- **Diagnostics:** Logs whether execution used a real model or was simulated (e.g., when model is missing from context).

### `MLXSynchronizationOperation`
- **Purpose:** Evaluates deferred computation graphs.
- **Inputs:** Implicit dependency on preceding operations.
- **Outputs:** None.
- **Diagnostics:** Indicates if `mx.eval()` was successfully invoked.

### `MLXCacheLookupOperation`
- **Purpose:** Resolves historical token cache dependencies (e.g., Prefill phase).
- **Diagnostics:** "Cache lookup handled via implicit MLX graph."

### `MLXCacheUpdateOperation`
- **Purpose:** Commits new token key-values to the ongoing request cache (e.g., Decode phase).
- **Diagnostics:** "Cache update handled via implicit MLX graph."

### `MLXSamplingOperation`
- **Purpose:** Architectural placeholder for token selection.
- **Constraints:** Explicitly rejected by the backend to enforce the rule that Sampling belongs to the Runtime. Returns an `unsupported` status.

### `MLXNoOpOperation`
- **Purpose:** Safely handles auxiliary or unsupported physical operations without crashing the pipeline.

## Execution Return Structure
All operations return a standard dictionary:
```python
{
    "status": "executed" | "unsupported" | "failed",
    "operation_id": "str",
    "backend": "mlx",
    "diagnostics": ["list of strings"],
    "execution_duration_ms": float,
    "error": "optional error string",
    "result": {"arbitrary": "data"}
}
```
