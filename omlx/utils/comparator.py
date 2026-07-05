# SPDX-License-Identifier: Apache-2.0
"""
Canonical artifact comparator.
"""
from typing import Any, Dict, Tuple
from omlx.utils.serialization import serialize_artifact

def diff_structures_nested(old_data: Any, new_data: Any) -> Dict[str, Any]:
    """Recursively diffs two serialized objects, generating nested difference maps."""
    old_serialized = serialize_artifact(old_data)
    new_serialized = serialize_artifact(new_data)

    diff = {"added": {}, "removed": {}, "changed": {}}

    if not isinstance(old_serialized, dict) or not isinstance(new_serialized, dict):
        if old_serialized != new_serialized:
            return {"added": {}, "removed": {}, "changed": {"": {"from": old_serialized, "to": new_serialized}}}
        return diff

    old_keys = set(old_serialized.keys())
    new_keys = set(new_serialized.keys())

    for k in new_keys - old_keys:
        diff["added"][k] = new_serialized[k]

    for k in old_keys - new_keys:
        diff["removed"][k] = old_serialized[k]

    for k in old_keys & new_keys:
        v_old = old_serialized[k]
        v_new = new_serialized[k]

        if isinstance(v_old, dict) and isinstance(v_new, dict):
            sub_diff = diff_structures_nested(v_old, v_new)
            if any(sub_diff.values()):
                diff["changed"][k] = sub_diff
        elif v_old != v_new:
            diff["changed"][k] = {"from": v_old, "to": v_new}

    return diff


def diff_structures_flat(actual: Any, expected: Any, prefix: str = "") -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Recursively compares two structures, returning flat maps of differences with dot-separated paths."""
    actual_serialized = serialize_artifact(actual)
    expected_serialized = serialize_artifact(expected)

    added: Dict[str, Any] = {}
    removed: Dict[str, Any] = {}
    changed: Dict[str, Any] = {}

    def dict_diff(d1: Any, d2: Any, path: str):
        if not isinstance(d1, dict) or not isinstance(d2, dict):
            if d1 != d2:
                changed[path] = {"actual": d1, "expected": d2}
            return

        for k, v1 in d1.items():
            p = f"{path}.{k}" if path else k
            if k not in d2:
                added[p] = v1
            elif isinstance(v1, dict) and isinstance(d2[k], dict):
                dict_diff(v1, d2[k], p)
            elif v1 != d2[k]:
                changed[p] = {"actual": v1, "expected": d2[k]}

        for k, v2 in d2.items():
            p = f"{path}.{k}" if path else k
            if k not in d1:
                removed[p] = v2

    dict_diff(actual_serialized, expected_serialized, prefix)
    return added, removed, changed
