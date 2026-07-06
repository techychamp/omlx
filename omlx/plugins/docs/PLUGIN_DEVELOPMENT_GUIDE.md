# Plugin Development Guide

## Getting Started
To create an OMLX plugin, implement the following two requirements in your module:
1. Expose a `get_descriptor()` function returning a `PluginDescriptor`.
2. Expose an `initialize_plugin(context)` function.

## Defining the Descriptor
```python
from omlx.plugins.descriptor import PluginDescriptor, PluginCapability, PluginPermission, PluginCategory

def get_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        plugin_id="my.custom.sampler",
        name="Custom Sampler",
        version="1.0.0",
        author="OMLX Developer",
        description="Provides specialized sampling algorithms.",
        category=PluginCategory.CAPABILITY,
        capabilities=(PluginCapability.PLANNER_EXTENSION.value,),
        permissions=(PluginPermission.PLANNER_ACCESS.value,),
    )
```

## Initializing and Registering Extensions
```python
from omlx.plugins.context import PluginInitializationContext

class MyCustomSamplerExtension:
    # Must implement the relevant ExtensionPoint protocol
    pass

def initialize_plugin(context: PluginInitializationContext):
    extension = MyCustomSamplerExtension()
    context.register_extension(extension)
```

## Publishing
Expose your plugin via standard Python `entry_points` in your `pyproject.toml` or `setup.py` under the group `omlx.plugins`.
