## Summary
Implemented Capability Resolver to centralize capability logic in oMLX.

## Architecture impact
This is an infrastructure update according to IMP-005, introducing the `CapabilityResolver` which is integrated with `RuntimeBuilder`. Capability logic is now resolved deterministically and outputs an immutable `CapabilityDescriptor`.

## Files changed
- `omlx/capabilities/__init__.py` (Added)
- `omlx/capabilities/descriptor.py` (Added)
- `omlx/capabilities/exceptions.py` (Added)
- `omlx/capabilities/merge.py` (Added)
- `omlx/capabilities/resolver.py` (Added)
- `omlx/capabilities/sources.py` (Added)
- `omlx/capabilities/validation.py` (Added)
- `tests/test_capability_resolver.py` (Added)
- `IMP-005-Capability-Resolver-Report.md` (Added)
- `capabilities_walkthrough.md` (Added)
- `omlx/runtime/builder.py` (Modified)

## Verification evidence
- 7 tests passing in `tests/test_capability_resolver.py`, validating sources, merge precedence, logic validation, and exception raising.

## Risks
Low risk, as legacy mechanisms for dictionary parsing inside patches are still present. This lays the groundwork for them to be safely replaced later in IMP-006.

## Remaining work
Implement EventBus in a future task.

## Recommendation
Approve and commit.

## Confidence
High.
