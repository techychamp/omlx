# SPDX-License-Identifier: Apache-2.0
"""
Compiler Cache Utilities for generating deterministic cache keys.
"""

from typing import Any
from omlx.utils.hashing import compute_stable_hash

def compute_cache_key(prefix: str, artifact: Any) -> str:
    """
    Computes a deterministic, content-based SHA-256 cache key.
    """
    digest = compute_stable_hash(artifact)
    return f"{prefix}_{digest}"

