# Async Guide

The oMLX SDK provides native asynchronous methods designed to integrate seamlessly into modern Python workflows (e.g., FastAPI, Starlette).

## Async Execution
All potentially blocking operations expose an `_async` variant. We utilize `asyncio.to_thread` to safely offload heavy compilations or planning algorithms out of the main event loop.

```python
import asyncio
from omlx.api.v1 import CompilerRequestBuilder, Compiler

async def compile_model():
    request = CompilerRequestBuilder().with_model("my-model").build_request()
    compiler = Compiler()

    # Non-blocking compilation
    result = await compiler.compile_async(request)
    print(f"Compilation success: {result.success}")
```
