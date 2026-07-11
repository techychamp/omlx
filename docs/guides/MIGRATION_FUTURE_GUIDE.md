# Migration and Future Extension Guide

## Current Status
The plugin framework (PLUGIN-001 through PLUGIN-005) successfully replaces the hardcoded backend and sampler architectures. Core OMLX components now retrieve capabilities dynamically from the sealed `PluginRegistry`.

## Future Proofing
The framework is designed to natively support:
- `PLUGIN-006`
- `GUI-001` / `WORKBENCH-001`
- `APPLE-001` / `SPEC-001`

Adding support for new ML models or advanced hardware requires NO modifications to `src/omlx/core`. A developer simply implements the `BackendPlugin` or `PlannerPlugin` protocol, defines a `PluginDescriptor`, and exposes it via an entry point.
