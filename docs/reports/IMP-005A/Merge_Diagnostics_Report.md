# Merge Diagnostics Report

## Introduction
The capability merging engine historically updated dictionaries with standard precedence but failed to record origin tracking, meaning it was impossible to easily distinguish if an attribute like `supports_streaming=True` originated from a plugin or a feature flag.

## Diagnostics Implementation
1. **`CapabilityProvenance`**: A structured dataclass explicitly tracking the `value`, `winner` (final overriding source), and `history` (list of contributing sources from lowest to highest precedence) for each resolved capability key.
2. **`MergeResult`**: The `merge_sources()` routine now returns this wrapped data object that holds both `merged_values` (the standard operational configuration) and `diagnostics` (a dictionary mapping capability keys to `CapabilityProvenance`).

## Visibility
The diagnostic history is successfully bundled into a private attribute on the resulting `CapabilityDescriptor` named `_diagnostics`. By enforcing this isolation:
- The public `resolve()` API surface does not change.
- There are no runtime performance overheads inside execution systems.
- Provenance details are strongly structured and easily available for logging, verification frameworks, or debugging APIs when diagnosing misconfigured plugins or overlapping capabilities.
