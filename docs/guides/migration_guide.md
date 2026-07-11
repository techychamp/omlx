# Migration Guide (to v1)

If you were previously relying on internal oMLX imports (e.g., directly importing `ExecutionPlanner` from `omlx.planner`), this guide helps you migrate to the stable `omlx.api.v1` SDK.

## Key Changes
1. **Stop Importing Internals**: Internal packages like `omlx.runtime`, `omlx.planner`, and `omlx.compiler` should no longer be imported.
2. **Use Builders**: Instead of constructing raw dictionaries or passing configurations directly to engines, use the provided fluent builders.
3. **Handle Typed Models**: Results are now strongly-typed Pydantic models, not generic dictionaries.

## Before and After
*Before:*
```python
from omlx.planner.planner import ExecutionPlanner
planner = ExecutionPlanner(...)
plan = planner.plan(descriptor)
```

*After:*
```python
from omlx.api.v1 import PlanningRequestBuilder, Planner
request = PlanningRequestBuilder().with_model("model-id").build_request()
result = Planner().plan(request)
```
