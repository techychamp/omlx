import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any, Dict

def _normalize_value(value: Any) -> Any:
    """Recursively normalize values for stable hashing."""
    if isinstance(value, dict):
        return {k: _normalize_value(v) for k, v in sorted(value.items())}
    elif isinstance(value, (list, tuple, set, frozenset)):
        # For sets, we sort them if the elements are sortable
        try:
            return sorted(_normalize_value(v) for v in value)
        except TypeError:
            # Fallback if elements are not mutually comparable
            return [_normalize_value(v) for v in value]
    elif is_dataclass(value):
        return _normalize_value(asdict(value))
    elif hasattr(value, "__dict__"):
        return _normalize_value(value.__dict__)
    elif hasattr(value, "value"): # For Enums
        return value.value
    else:
        return value

class CacheKey:
    """
    Generates a deterministic hash key for cache entries.
    Avoids object identity and mutable state.
    """
    def __init__(self, **kwargs):
        self.inputs = kwargs
        self._hash = None

    def compute_hash(self) -> str:
        if self._hash is None:
            normalized = _normalize_value(self.inputs)
            serialized = json.dumps(normalized, sort_keys=True)
            self._hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return self._hash

    def __str__(self):
        return self.compute_hash()

    def __repr__(self):
        return f"CacheKey(hash={self.compute_hash()}, inputs={self.inputs.keys()})"
