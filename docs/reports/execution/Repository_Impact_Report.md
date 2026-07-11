# Repository Impact Report

- **`omlx/capabilities/descriptor.py`**:
  - Imported `types.MappingProxyType`.
  - Added recursive `freeze_value()` utility.
  - Added private `_diagnostics` field explicitly ignored by `repr`, `hash`, and `compare`.
  - Overhauled `__post_init__` to apply `freeze_value` to all dataclass properties dynamically via reflection.
- **`omlx/capabilities/merge.py`**:
  - Introduced `CapabilityProvenance` and `MergeResult`.
  - Upgraded `merge_sources()` to aggregate capability history alongside standard values.
- **`omlx/capabilities/validation.py`**:
  - Refactored `validate_capabilities` logic into Extensible Pipeline classes: `ValidationRule`, `ValidationRegistry`, `ValidationEngine`, and 4 concrete rules.
- **`omlx/capabilities/resolver.py`**:
  - Modified constructor to initialize `ValidationEngine` from optional rule overrides.
  - Adjusted `resolve()` to unpack `MergeResult` internally and supply diagnostics to the `CapabilityDescriptor` constructor.
- **`tests/test_capability_resolver.py`**:
  - Added coverage for Deep Immutability nested restrictions.
  - Added coverage for custom extensible validation.
  - Added coverage for thread safety and provenance extraction.
