# SPDX-License-Identifier: Apache-2.0
"""
Bundle Export functionality.
"""
import os
import json
from typing import Any
from dataclasses import asdict, is_dataclass
from types import MappingProxyType

def _custom_dict_factory(data):
    # This is passed a list of (field_name, field_value) tuples
    d = {}
    for k, v in data:
        if isinstance(v, MappingProxyType):
            d[k] = {kk: _serialize(vv) for kk, vv in v.items()}
        else:
            d[k] = _serialize(v)
    return d

def _serialize(obj: Any) -> Any:
    # Extremely basic serialization for demonstration
    if is_dataclass(obj):
        # We use asdict with a custom dict_factory to avoid deepcopy mappingproxy issues
        return asdict(obj, dict_factory=_custom_dict_factory)
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
    def export(observer_or_session: Any, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)

        if hasattr(observer_or_session, 'get_trace'):
            trace = observer_or_session.get_trace()
            telemetry = observer_or_session.get_telemetry()
            bundle = observer_or_session.get_artifacts()
            timeline = observer_or_session.get_timeline() if hasattr(observer_or_session, 'get_timeline') else None
        else:
            trace = observer_or_session.trace
            telemetry = observer_or_session.telemetry
            bundle = observer_or_session.artifacts
            timeline = observer_or_session.timeline

        # Export Trace
        with open(os.path.join(output_dir, "trace.json"), "w") as f:
            json.dump(_serialize(trace), f, indent=2)

        # Export Timeline
        if timeline:
            with open(os.path.join(output_dir, "timeline.json"), "w") as f:
                json.dump(_serialize(timeline), f, indent=2)

        # Export Telemetry
        with open(os.path.join(output_dir, "statistics.json"), "w") as f:
            out = {
                "measurements": dict(telemetry.measurements),
                "counters": dict(telemetry.counters)
            }
            json.dump(out, f, indent=2)

        # Export Artifacts
        artifacts_dir = os.path.join(output_dir, "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)

        for name, artifact in bundle.artifacts.items():
            path = os.path.join(artifacts_dir, f"{name}.json")
            with open(path, "w") as f:
                json.dump(_serialize(artifact), f, indent=2)
