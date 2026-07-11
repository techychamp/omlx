# Lifecycle Management Guide

## Overview
Backends are not all equal in stability. The Lifecycle framework provides a `BackendLifecycleState` enum attached to every registration in the `AdapterRegistry`.

## States
- **REGISTERED**: Available but not yet fully initialized/validated.
- **AVAILABLE**: Ready for selection.
- **UNAVAILABLE**: Temporarily or permanently offline (e.g. missing drivers).
- **INITIALIZING**: Currently warming up.
- **DEPRECATED**: Valid but scheduled for removal.
- **EXPERIMENTAL**: Valid but not recommended for production.
- **DISABLED**: Explicitly turned off via configuration.
- **PLUGIN**: Loaded via a third-party extension.

## Usage
The `AdapterRegistry.resolve()` method now avoids returning `UNAVAILABLE` or `DISABLED` backends. The selection framework ignores them or penalizes them.
