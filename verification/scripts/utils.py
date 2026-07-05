# SPDX-License-Identifier: Apache-2.0
"""Verification Framework Utilities."""

import json
import os
from typing import Any, Dict, List, Optional
from dataclasses import is_dataclass, asdict
from types import MappingProxyType

class GoldenLoader:
    @staticmethod
    def load(path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Golden asset not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save(data: dict, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

class ArtifactSerializer:
    @staticmethod
    def serialize(obj: Any) -> dict:
        from omlx.utils.serialization import serialize_artifact
        return serialize_artifact(obj)

class ArtifactDiff:
    def __init__(self, added: dict, removed: dict, changed: dict):
        self.added = added
        self.removed = removed
        self.changed = changed

    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def to_dict(self) -> dict:
        return {
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed
        }

class GoldenComparator:
    @staticmethod
    def compare(actual: Any, expected: Any, path: str = "") -> ArtifactDiff:
        from omlx.utils.comparator import diff_structures_flat
        added, removed, changed = diff_structures_flat(actual, expected, path)
        return ArtifactDiff(added, removed, changed)

