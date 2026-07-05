# SPDX-License-Identifier: Apache-2.0
"""
Canonical artifact serializer.
"""
from typing import Any
from dataclasses import is_dataclass
from types import MappingProxyType

def serialize_artifact(obj: Any) -> Any:
    """Recursively serialize arbitrary compiler/runtime artifacts into JSON-serializable primitives."""
    if hasattr(obj, "to_dict"):
        return serialize_artifact(obj.to_dict())
    if is_dataclass(obj):
        # Convert dataclasses to dict by reading their fields, avoiding deepcopy of MappingProxyType
        fields_dict = {f: getattr(obj, f) for f in obj.__dataclass_fields__}
        return serialize_artifact(fields_dict)
    if isinstance(obj, (dict, MappingProxyType)):
        return {str(k): serialize_artifact(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [serialize_artifact(item) for item in obj]
    if hasattr(obj, "value"):  # Enums
        return obj.value
    if hasattr(obj, "__dict__"):
        return serialize_artifact(obj.__dict__)
    return obj
