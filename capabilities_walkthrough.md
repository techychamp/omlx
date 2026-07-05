# Capability Resolution Walkthrough

## Overview
The `CapabilityResolver` standardizes how model execution capabilities (e.g., attention types, modality support, family) are discovered and structured in oMLX.

### Flow of Resolution
1. **Instantiation**: At startup, `RuntimeBuilder` creates a `CapabilityResolver` with default fallback sources (e.g., global feature flags).
2. **Context Resolution**: When a request to load or execute a model arrives, `CapabilityResolver.resolve()` is called.
3. **Gathering Sources**: The resolver aggregates capability metadata from multiple independent sources (`ModelMetadataSource`, `PluginSource`, `FeatureFlagSource`, `RuntimeOverrideSource`).
4. **Merge Engine**: Sources are iteratively merged. Later sources in the priority list override earlier sources.
    - Priority: Defaults < Model Metadata < Adapter < Plugins < Feature Flags < Runtime Overrides.
5. **Validation Engine**: The merged dictionary is strictly validated to ensure logical consistency (e.g., blocking `streaming` for `diffusion` models).
6. **Descriptor Generation**: The validated dictionary is serialized into an immutable, frozen `CapabilityDescriptor`.
7. **Consumption**: Subsystems (Planners, Adapters) receive this `CapabilityDescriptor` instead of parsing raw model `.json` configurations.
