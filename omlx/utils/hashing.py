# SPDX-License-Identifier: Apache-2.0
"""
Deterministic stable hashing utility.
"""
import json
import hashlib
from typing import Any
from omlx.utils.serialization import serialize_artifact

def compute_stable_hash(artifact: Any) -> str:
    """Computes a deterministic content-based SHA-256 hash for arbitrary artifacts."""
    serialized = serialize_artifact(artifact)
    
    # Stable JSON serialization with sorted keys
    json_str = json.dumps(serialized, sort_keys=True)
    
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()
