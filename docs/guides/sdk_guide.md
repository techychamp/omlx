# SDK Guide

Welcome to the oMLX API v1 SDK. This guide covers the basics of integrating with oMLX programmatically.

## Philosophy
The SDK strictly encapsulates internal implementations. It provides fluent builder patterns for constructing requests and strongly-typed models for processing results. You will never need to instantiate internal components like `ExecutionPlanner` or `CompilerEngine` directly.

## Getting Started

```python
from omlx.api.v1 import RuntimeBuilder

runtime = RuntimeBuilder().configure({"mode": "production"}).build()
print(f"Runtime is {runtime.state}")
```
