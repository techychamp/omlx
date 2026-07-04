# MLX Reference Backend Walkthrough

The `MLXAdapter` serves as the blueprint for how hardware/framework-specific implementations connect to OMLX.

1. **Instantiation:** `MLXAdapter` initializes an immutable `BackendDescriptor`. This descriptor contains extensive metadata about the MLX implementation (e.g., Apple Silicon hardware, unified memory model).
2. **Capabilities:** The adapter advertises capabilities using `BackendCapability` (e.g., `AUTOREGRESSIVE`, `PAGED_KV_CACHE`).
3. **Validation:** The `validate` method checks a `PhysicalIR` graph. It returns a rich `BackendValidationResult`, verifying unsupported operations, execution families, and missing capabilities.
4. **Translation:** The `translate` method transforms a `PhysicalIR` into a `BackendOperationGraph` comprised of `MLXOperation` subclasses (e.g., `MLXForwardOperation`, `MLXSynchronizationOperation`). It returns a `TranslationResult` tracking translation latency and operational statistics.
