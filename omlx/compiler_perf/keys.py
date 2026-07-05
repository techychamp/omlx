# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict
from omlx.utils.hashing import compute_stable_hash

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
            self._hash = compute_stable_hash(self.inputs)
        return self._hash

    def __str__(self):
        return self.compute_hash()

    def __repr__(self):
        return f"CacheKey(hash={self.compute_hash()}, inputs={self.inputs.keys()})"

