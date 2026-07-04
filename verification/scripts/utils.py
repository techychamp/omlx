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
        if hasattr(obj, "to_dict"):
            return ArtifactSerializer.serialize(obj.to_dict())
        if is_dataclass(obj):
            # Convert to dict manually to avoid deepcopy issues with mappingproxy
            d = {f: getattr(obj, f) for f in obj.__dataclass_fields__}
            return ArtifactSerializer.serialize(d)
        if isinstance(obj, MappingProxyType):
            return {k: ArtifactSerializer.serialize(v) for k, v in obj.items()}
        if isinstance(obj, dict):
            return {k: ArtifactSerializer.serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [ArtifactSerializer.serialize(item) for item in obj]
        return obj

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
        actual_dict = ArtifactSerializer.serialize(actual)
        expected_dict = ArtifactSerializer.serialize(expected)

        added, removed, changed = {}, {}, {}

        def dict_diff(d1: dict, d2: dict, prefix: str):
            for k, v1 in d1.items():
                p = f"{prefix}.{k}" if prefix else k
                if k not in d2:
                    added[p] = v1
                elif isinstance(v1, dict) and isinstance(d2[k], dict):
                    dict_diff(v1, d2[k], p)
                elif v1 != d2[k]:
                    changed[p] = {"actual": v1, "expected": d2[k]}

            for k, v2 in d2.items():
                p = f"{prefix}.{k}" if prefix else k
                if k not in d1:
                    removed[p] = v2

        dict_diff(actual_dict, expected_dict, path)
        return ArtifactDiff(added, removed, changed)
