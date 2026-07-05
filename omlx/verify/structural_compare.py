# SPDX-License-Identifier: Apache-2.0
"""
VERIFY Structural Comparison Engine
Provides generic structural comparison for any compiler artifact.
"""
from typing import Any
import json

class StructuralComparator:
    """Base class for generic structural comparison."""

    def compare(self, old_artifact: Any, new_artifact: Any) -> dict[str, Any]:
        """Compares two arbitrary compiler artifacts by serializing them to dicts."""
        if hasattr(old_artifact, "to_dict"):
            old_dict = old_artifact.to_dict()
        elif hasattr(old_artifact, "__dict__"):
            old_dict = old_artifact.__dict__
        else:
            old_dict = {"value": old_artifact}

        if hasattr(new_artifact, "to_dict"):
            new_dict = new_artifact.to_dict()
        elif hasattr(new_artifact, "__dict__"):
            new_dict = new_artifact.__dict__
        else:
            new_dict = {"value": new_artifact}

        # sanitize to generic serializable structures before dict comparison
        return self.diff_dicts(self._sanitize(old_dict), self._sanitize(new_dict))

    def _sanitize(self, d: Any) -> Any:
        if isinstance(d, dict):
            return {k: self._sanitize(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple, set)):
            return [self._sanitize(v) for v in d]
        elif hasattr(d, "value"): # Enum handling
            return d.value
        else:
            return d

    def diff_dicts(self, old_data: dict[str, Any], new_data: dict[str, Any]) -> dict[str, Any]:
        """Generic recursive dictionary differ."""
        diff = {"added": {}, "removed": {}, "changed": {}}

        old_keys = set(old_data.keys())
        new_keys = set(new_data.keys())

        for k in new_keys - old_keys:
            diff["added"][k] = new_data[k]

        for k in old_keys - new_keys:
            diff["removed"][k] = old_data[k]

        for k in old_keys & new_keys:
            v_old = old_data[k]
            v_new = new_data[k]

            if isinstance(v_old, dict) and isinstance(v_new, dict):
                sub_diff = self.diff_dicts(v_old, v_new)
                if any(sub_diff.values()):
                    diff["changed"][k] = sub_diff
            elif v_old != v_new:
                 diff["changed"][k] = {"from": v_old, "to": v_new}

        return diff
