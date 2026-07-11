# Known Limitations

Following the implementation of BACKEND-005, the following limitations remain:

1. **Dummy Inputs for Forward Passes:**
   While `MLXAdapter.execute()` performs real kernel dispatch against `context.model`, the OMLX runtime does not yet fully populate `ExecutionContext.request_context.input_ids`. As a result, the adapter falls back to executing the model with a dummy `[0]` input tensor to prove structural correctness.
2. **Phase A vs Phase B Generation:**
   The compiler pipeline (Phase A) executes the backend operation graph correctly and evaluates forward passes. However, token generation (decode loops) still relies on the compatibility shim (Phase B) using `mlx_lm.generate()`. The compiler is not yet driving the step-by-step autoregressive decode loop.
3. **KV Cache Handling:**
   `MLXCacheLookupOperation` and `MLXCacheUpdateOperation` are currently handled via implicit state within the MLX computation graph. The adapter does not explicitly manage or slice the KV cache memory tensors. True paging or advanced cache management will require bridging MLX cache structures with the compiler's logical view.
4. **Sampling Execution:**
   Sampling operations are correctly rejected by the backend. However, the runtime does not yet have a fully native OMLX sampler implemented to catch and process the logits returned by the backend.
