# Diagnostics Documentation

The `DiagnosticsTracker` collects `OptimizationDiagnostic` objects during pipeline execution.

## Supported Levels
- INFO, WARNING, ERROR, DEBUG

## Usage
Passes should use `context.tracker.add_diagnostic(...)` to report issues, skipped optimizations, or successful canonicalizations.
