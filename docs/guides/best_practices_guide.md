# Best Practices Guide

1. **Always Use Async in Servers**: If you are integrating the SDK into FastAPI or an asynchronous HTTP server, strictly use the `*_async` methods (e.g., `compile_async()`) to avoid blocking the event loop.
2. **Build Requests Defensively**: Use the provided Builders (`CompilerRequestBuilder`, etc.) rather than manually constructing models, as builders enforce business logic and defaults.
3. **Handle SDK Exceptions**: Always wrap SDK calls in a `try...except OmlxError:` block to gracefully degrade upon compiler or planning failures.
4. **Never Expose Internals**: Do not attempt to bypass the SDK by accessing `_internal_runtime` or `_engine`. This will cause compatibility breaks in future minor versions.
