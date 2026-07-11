# Compatibility Guide

The `omlx.api.v1` SDK exposes the `check_api_compatibility` utility to verify script and plugin compatibility with the current release.

## Usage
```python
from omlx.api.v1 import check_api_compatibility

report = check_api_compatibility("v1")
if not report.is_compatible:
    print(f"Breaking changes: {report.breaking_changes}")
```

## Guarantees
* The `v1` namespace promises semantic versioning.
* Internal architecture changes will not break `v1` contracts.
