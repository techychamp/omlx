# Lifecycle, Dependencies, and Capabilities Guide

## Plugin Lifecycle
Plugins traverse a deterministic state machine:
1. `DISCOVERED`: The `PluginManager` found the entry point.
2. `REGISTERED`: Descriptor was read and added to the `PluginRegistry`.
3. `LOADED`: The Python module is safely loaded.
4. `INITIALIZED`: `initialize_plugin()` executes.
5. `VALIDATED`: Dependency graphs and API compatibilities are confirmed.
6. `ENABLED`: The registry is sealed, and the plugin is active.

Failures at any stage route the plugin to the isolated `FAILED` state, preventing corruption of the runtime.

## Dependency Resolution
Plugins declare dependencies via `dependencies` and `optional_dependencies` (Mapping of plugin_id -> semantic version).
The `PluginDependencyResolver` automatically generates a directed acyclic graph (DAG) to determine optimal loading order.
If circular dependencies or version mismatches are detected, affected plugins transition to `FAILED`.

## Capability Registration
Instead of resolving plugin names, OMLX operates on capabilities. Plugins declare supported functionalities (e.g., Apple Silicon support) via `PluginCapability`. The runtime queries the registry for these capabilities, enabling decoupled extension substitution.
