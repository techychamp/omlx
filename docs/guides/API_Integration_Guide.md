# API Integration Guide

## Principles
1. **Never bypass public APIs**. The Workbench should behave like an external client.
2. **Never invoke private methods (`_method()`)** on backend structures.

## Consuming OMLXClient
Instantiate the `DeveloperWorkbench` with an instance of `OMLXClient`.

```python
from omlx.api.v1.client import OMLXClient
from omlx.workbench import DeveloperWorkbench

client = OMLXClient()
workbench = DeveloperWorkbench(client)

dashboard_data = workbench.get_module_data("dashboard")
print(dashboard_data)
```

## Expanding API Coverage
If a module requires data not exposed by `OMLXClient`, the `OMLXClient` wrapper must be updated first, ensuring the data is exposed securely and immutably.
