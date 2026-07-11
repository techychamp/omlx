# Builder Guide

The `omlx.api.v1` SDK utilizes fluent builder patterns to simplify the construction of complex requests while ensuring immutability and valid states.

## Example: Compiler Request

```python
from omlx.api.v1 import CompilerRequestBuilder

request = (
    CompilerRequestBuilder()
    .with_model("llama-3-8b")
    .with_backend("mlx")
    .enable_optimization("flash_attention")
    .build_request()
)
```

Always use builders rather than constructing Request or Configuration models directly, as builders encapsulate necessary validation logic.
