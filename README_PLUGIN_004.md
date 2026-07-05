# PLUGIN-004 Documentation

This document describes the newly implemented plugin production readiness architecture components.

## Dependency Resolution
- Added `PluginDependencyResolver` in `omlx/plugins/resolver.py` to construct a deterministic plugin dependency graph without executing any code.
- Added `PluginDependencyGraph` and `PluginDependencyNode` in `omlx/plugins/graph.py` which are immutable dataclasses representing the relationships between plugins. The graph performs topological sorting and cycle detection.

## Registry Extensibility
- Added `PluginRegistryExtensions` in `omlx/plugins/extensions.py` to allow querying the plugin registry based on capabilities, permissions, trust level, compiler stages, and backends.

## Trust Enforcement Architecture
- Updated `omlx/plugins/descriptor.py` to add `PluginTrustLevel` enum (`CORE`, `BUILT_IN`, `VERIFIED`, `SIGNED`, `THIRD_PARTY`).
- A `trust_level` field exists on `PluginDescriptor` to enforce this policy architecturally.

## Permission Enforcement Architecture
- Updated `omlx/plugins/descriptor.py` to add `PluginPermission` enum (`COMPILER_ACCESS`, `PLANNER_ACCESS`, etc.).
- A `permissions` field on `PluginDescriptor` enforces capability and permission alignment statically.

## Sandbox Architecture
- Added `PluginSandboxPolicy` and `SandboxIsolationLevel` in `omlx/plugins/sandbox.py`. These are strictly immutable configuration options to outline isolation intents (`READ_ONLY`, `PROCESS_ISOLATION`, `WASM_EXECUTION`, etc.), without executing sandbox mechanisms.

## Lifecycle Monitoring
- Added `PluginLifecycleMonitor` in `omlx/plugins/lifecycle.py` to track state transitions and aggregate lifecycle counts (`REGISTERED`, `LOADED`, `FAILED`, etc.).

## Event Models
- Defined future event data classes in `omlx/plugins/events.py` (`PluginDiscovered`, `PluginLoaded`, etc.).

## Diagnostics & Statistics
- Added `PluginDiagnosticsGenerator` in `omlx/plugins/diagnostics.py` to compile graphs, permission usage, and trust levels.
- Added `PluginStatisticsCollector` in `omlx/plugins/statistics.py` to track the depth of the dependency graph and plugin distributions.
