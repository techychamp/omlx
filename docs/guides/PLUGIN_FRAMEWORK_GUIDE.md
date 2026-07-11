# Plugin Framework Guide

## Overview
The OMLX Plugin Framework provides a strictly controlled, declarative mechanism for extending the compiler and execution runtime. It enforces architectural isolation—plugins may extend functionality but must never replace the ownership of core domains (Compiler, Runtime, Backend).

## Core Concepts
1. **Descriptors**: Every plugin exposes a strictly immutable `PluginDescriptor` detailing identity, capabilities, and security boundaries.
2. **Registry**: The `PluginRegistry` manages registered plugins, dependencies, and resolved extension points. The registry seals upon runtime initialization, preventing global mutable state injection.
3. **Manager**: The `PluginManager` handles safe plugin discovery via `entry_points`, dynamic module loading, and deterministic initialization.
4. **Extension Points**: Core services query the registry for specific extension types (e.g., `BackendPlugin`, `QuantizationPlugin`) rather than hardcoding plugin names.

## Isolation and Thread Safety
Plugins execute in a read-only context during normal operations. Shared state is explicitly prohibited by default via `PluginIsolationPolicy`. The capability registry relies on concurrent, thread-safe structures for resolving extension points.
