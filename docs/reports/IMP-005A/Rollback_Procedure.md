# Rollback Procedure

Since IMP-005A does not interact with outer layers and is strictly isolated to the internal architectural hardening of the `omlx/capabilities` module, a rollback consists of reverting the modified files to their previous stable states:

1. Restore `omlx/capabilities/descriptor.py` to its previous `@dataclass` format without `_diagnostics` or `freeze_value()`.
2. Restore `omlx/capabilities/merge.py` to return purely `dict[str, Any]` rather than `MergeResult`.
3. Restore `omlx/capabilities/validation.py` back to the procedural `validate_capabilities(caps)` hardcoded block.
4. Remove references to the Validation abstractions and `merge_result` unpacking in `omlx/capabilities/resolver.py`.
5. Remove test cases testing immutability, thread-safety, and provenance in `tests/test_capability_resolver.py`.

No modifications were applied to `RuntimeBuilder`, meaning it will continue utilizing `CapabilityResolver` identically post-rollback.
