# Navigation Guide

## NavigationManager
`NavigationManager` serves as the central router for Workbench modules. It allows dynamic registration and discovery of modules.

## Example
```python
from omlx.workbench import NavigationManager, WorkbenchModule, ModuleInfo

nav = NavigationManager()
module = WorkbenchModule(ModuleInfo(
    id="custom_view",
    name="Custom View",
    description="A specialized module.",
    route="/custom"
))

nav.register_module(module)
print(nav.list_modules())
```
