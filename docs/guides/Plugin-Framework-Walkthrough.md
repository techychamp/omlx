# Plugin Framework Walkthrough

## Overview

The oMLX Plugin Framework (PLUGIN-001) provides a canonical extension mechanism for the oMLX compiler, planner, backend, and tooling, without requiring modifications to the core framework code.

The architecture centers around these concepts:
- **`PluginDescriptor`**: An immutable metadata class defining a plugin's identity, dependencies, and provided capabilities.
- **`ExtensionPoint`**: A set of runtime-checkable Protocols (e.g., `BackendPlugin`, `OptimizationPlugin`) that plugins must implement to interact with the core.
- **`PluginContext`**: A read-only context passed to plugins during initialization, providing access to runtime state and a way to register extension instances.
- **`PluginRegistry`**: A central, thread-safe registry that handles plugin state transitions, dependency validation, and extension lookup.
- **`PluginManager`**: Orchestrates discovery (via Python entry points) and registry sealing.

## Developing a Plugin

### 1. Define the Plugin Module

A plugin module must expose two functions:
- `get_descriptor() -> PluginDescriptor`
- `initialize_plugin(context: PluginContext)`

```python
# my_plugin.py
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory
from omlx.plugins.context import PluginContext
from omlx.plugins.contracts import BackendPlugin

class MyCustomBackend(BackendPlugin):
    @property
    def extension_id(self) -> str:
        return "my_custom_backend_v1"

    def execute(self, ir):
        # Implementation here
        pass

def get_descriptor() -> PluginDescriptor:
    return PluginDescriptor(
        plugin_id="com.example.omlx.my_backend",
        name="Example Custom Backend",
        version="1.0.0",
        author="Example Corp",
        description="A custom backend for oMLX",
        category=PluginCategory.BACKEND
    )

def initialize_plugin(context: PluginContext):
    # Register the extension point
    context.register_extension(MyCustomBackend())
    context.add_diagnostic("custom_backend_loaded", True)
```

### 2. Register via Entry Points

In your plugin's `setup.py` or `pyproject.toml`, expose the entry point under the `omlx.plugins` group.

```toml
# pyproject.toml
[project.entry-points."omlx.plugins"]
my_custom_backend = "my_plugin"
```

## Lifecycle and Interaction

1. **Discovery:** During `RuntimeBuilder` bootstrap, `PluginManager.discover_plugins()` is called. It uses `importlib.metadata` to find entry points.
2. **Registration:** For each entry point, the descriptor is fetched and placed into the `PluginRegistry` with a state of `REGISTERED` -> `DISCOVERED`.
3. **Initialization:** `initialize_plugin(context)` is called. The plugin registers its extensions (e.g., `MyCustomBackend`). State becomes `INITIALIZED`.
4. **Validation:** `PluginManager.validate_and_seal()` checks dependencies (including circular ones). Valid plugins transition to `ENABLED`. The registry is sealed (immutable).
5. **Lookup:** Later, the core framework (e.g., `ExecutionPlanner`) asks the registry: `registry.get_extensions(BackendPlugin)`. It receives a list of all registered backend extensions to use.

## Immutability & Thread Safety

- **Immutability:** The `PluginDescriptor` is a `@dataclass(frozen=True)`. The `PluginRegistry` is sealed after bootstrap; any subsequent registration attempts raise a `RuntimeError`.
- **Thread Safety:** `PluginRegistry` uses an internal `RLock` for all write operations, ensuring parallel discovery (if implemented) is safe.

## Diagnostics

The `PluginRegistry` automatically collects diagnostics on:
- Registration success/failure.
- Dependency validation (missing deps, circular deps).
- Lifecycle state transitions.

These can be accessed via `PluginManager.get_diagnostics()` and integrated into the `TOOLING` or `VERIFY` subsystems.
