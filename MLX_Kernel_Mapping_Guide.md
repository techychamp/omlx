# MLX Kernel Mapping Guide

This guide documents the mapping from OMLX compiler physical operations to real MLX kernels and backend actions in the `MLXAdapter`.

## Mappings

### 1. Forward Operation
- **Physical Operation:** `PhysicalOperationType.FORWARD`
- **Backend Operation:** `MLXForwardOperation`
- **MLX Execution:** Evaluates the model forward pass.
- **Kernel Dispatch:** `logits = context.model(input_ids)`
- **Note:** Real model weights and architecture dictates the underlying MLX kernels invoked (e.g., matrix multiplications, layer norms, non-linearities).

### 2. Synchronization Operation
- **Physical Operation:** `PhysicalOperationType.SYNCHRONIZATION`
- **Backend Operation:** `MLXSynchronizationOperation`
- **MLX Execution:** Triggers evaluation of the MLX compute graph to force execution on the GPU.
- **Kernel Dispatch:** `mx.eval()`
- **Note:** MLX builds computation graphs lazily. The synchronization barrier forces these graphs to evaluate, aligning with OMLX scheduling boundaries.

### 3. Cache Lookup / Update Operations
- **Physical Operation:** `PhysicalOperationType.CACHE_LOOKUP` / `CACHE_UPDATE`
- **Backend Operation:** `MLXCacheLookupOperation` / `MLXCacheUpdateOperation`
- **MLX Execution:** Handled implicitly via the MLX graph and KV cache objects passed to the model during the forward pass.
- **Kernel Dispatch:** Currently implemented as a successful execution that delegates to the implicit MLX graph evaluation during forward passes.

### 4. Sampling Operation
- **Physical Operation:** `PhysicalOperationType.SAMPLING`
- **Backend Operation:** `MLXSamplingOperation`
- **MLX Execution:** Unsupported.
- **Kernel Dispatch:** None.
- **Note:** Token sampling belongs to the runtime. The adapter actively rejects this operation with an `unsupported` status, maintaining the architectural boundary.

### 5. No-Op
- **Physical Operation:** Any unrecognized physical operation.
- **Backend Operation:** `MLXNoOpOperation`
- **MLX Execution:** None.
- **Kernel Dispatch:** Immediately returns an `executed` status.
