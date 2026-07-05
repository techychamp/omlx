# SPDX-License-Identifier: Apache-2.0
"""
Canonical deep freeze utility.
"""
from typing import Any
from types import MappingProxyType

def deep_freeze(obj: Any) -> Any:
    """Recursively freeze mutable structures into immutable/read-only views."""
    if isinstance(obj, (list, tuple)):
        return tuple(deep_freeze(x) for x in obj)
    elif isinstance(obj, (dict, MappingProxyType)):
        return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})
    elif isinstance(obj, set):
        return frozenset(deep_freeze(x) for x in obj)
    elif hasattr(obj, "value"):  # Enums
        return obj.value
    return obj
