# SPDX-License-Identifier: Apache-2.0
"""
Bundle Export functionality.
"""
import os
import json
from typing import Any
from dataclasses import asdict, is_dataclass
from types import MappingProxyType

def _serialize(obj: Any) -> Any:
    # Extremely basic serialization for demonstration
    if is_dataclass(obj):
        # We don't use asdict directly because of deepcopy mappingproxy issues
        result = {}
        for k, v in obj.__dict__.items():
            result[k] = _serialize(v)
        return result
    if isinstance(obj, MappingProxyType):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return _serialize(obj.__dict__)

    # Fallback to check if it's serializable, else stringify
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)

class BundleExporter:
    @staticmethod
    def export(observer: Any, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)

        # Export Trace
        trace = observer.get_trace()
        with open(os.path.join(output_dir, "trace.json"), "w") as f:
            json.dump(_serialize(trace), f, indent=2)

        # Export Telemetry
        telemetry = observer.get_telemetry()
        with open(os.path.join(output_dir, "statistics.json"), "w") as f:
            # Need to convert MappingProxyType to dict
            out = {
                "measurements": dict(telemetry.measurements),
                "counters": dict(telemetry.counters)
            }
            json.dump(out, f, indent=2)

        # Export Artifacts
        artifacts_dir = os.path.join(output_dir, "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        bundle = observer.get_artifacts()

        for name, artifact in bundle.artifacts.items():
            path = os.path.join(artifacts_dir, f"{name}.json")
            with open(path, "w") as f:
                json.dump(_serialize(artifact), f, indent=2)
