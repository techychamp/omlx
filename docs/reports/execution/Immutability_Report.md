# Immutability Report

## Issue
The original `CapabilityDescriptor` was frozen via Python's `@dataclass(frozen=True)` which prevented assignment to attributes. However, nested mutable types such as dictionaries (e.g. `execution_hints`) or lists could still be modified directly via index or key.

## Implementation Details
A new `freeze_value` function was added to `omlx/capabilities/descriptor.py`.
During `CapabilityDescriptor.__post_init__`, it iterates through all defined `__dataclass_fields__` and applies `freeze_value` recursively.

- `dict` types are safely converted into `types.MappingProxyType`.
- `list` types are recursively converted into `tuple`.
- `set` types are recursively converted into `frozenset`.

## Outcome
The descriptor is now **deeply immutable**. Attempts to modify `execution_hints["nested_key"]` or `attention_types[0]` will raise a `TypeError`, ensuring configuration integrity across the entire application pipeline and satisfying strict thread-safety expectations.
