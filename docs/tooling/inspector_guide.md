# Compiler Inspector Guide

## Overview
The `CompilerInspector` provides a unified read-only interface for examining internal compiler data structures. It prevents accidental mutation by strictly returning frozen/primitive dictionary representations of the requested artifacts.

## Supported Artifacts
- **CapabilityDescriptor**: Extracts capabilities and diagnostics, resolving enums to strings safely.
- **ExecutionPlan**: Returns plan hints, backends, and layout metadata.
- **Logical / Physical IR**: Leverages the IR's native `.to_dict()` serialization.

## Usage Rules
- **Do not** attempt to reconstruct live objects from the inspector's output. The output is intended for observability, diffing, and export.
- **Thread Safety**: The inspector holds no internal state and is safe to use across multiple threads simultaneously.
