# SPDX-License-Identifier: Apache-2.0
"""
Compiler Cache Utilities for generating deterministic cache keys.
"""

import hashlib
import json
from typing import Any

def compute_cache_key(prefix: str, artifact: Any) -> str:
    """
    Computes a deterministic, content-based SHA-256 cache key.
    Assumes the artifact implements to_dict() or can be serialized to JSON.
    """
    if hasattr(artifact, "to_dict"):
        data = artifact.to_dict()
    elif hasattr(artifact, "__dict__"):
        data = artifact.__dict__
    else:
        # Fallback to string representation for primitives/unhandled types
        data = str(artifact)

    try:
        # Sort keys to ensure deterministic canonical JSON
        # Instead of default=str which includes memory addresses for unhandled objects,
        # try to get a more deterministic representation
        def deterministic_default(obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            elif hasattr(obj, "items") and callable(obj.items):
                return dict(obj.items())
            elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
                return list(obj)
            return str(obj)

        json_str = json.dumps(data, sort_keys=True, default=deterministic_default)
    except Exception:
        # Ultimate fallback
        json_str = str(artifact)

    digest = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    return f"{prefix}_{digest}"
