import pytest
import os
import json
import shutil
from omlx.runtime.observability import Observer, BundleExporter

def test_observer_tracing():
    observer = Observer()
    with observer.observe_phase("Compilation", "Compiler", "Parse"):
        pass
    with observer.observe_phase("Execution", "Engine", "Run"):
        pass

    trace = observer.get_trace()
    assert len(trace.events) == 2
    assert trace.events[0].phase == "Compilation"
    assert trace.events[1].phase == "Execution"

def test_observer_artifacts():
    observer = Observer()
    observer.track_artifact("dummy_ir", {"nodes": [1, 2, 3]})
    artifacts = observer.get_artifacts()
    assert artifacts.artifacts["dummy_ir"]["nodes"] == [1, 2, 3]

def test_observer_telemetry():
    observer = Observer()
    with observer.observe_phase("Compilation", "Compiler", "Parse"):
        pass
    telemetry = observer.get_telemetry()
    assert telemetry.counters["Compilation.Parse.count"] == 1
    assert "Compilation.Parse.duration" in telemetry.measurements

def test_bundle_export():
    observer = Observer()
    with observer.observe_phase("Compilation", "Compiler", "Parse"):
        pass
    observer.track_artifact("dummy_ir", {"nodes": [1, 2, 3]})

    output_dir = "test_bundle_export"
    BundleExporter.export(observer, output_dir)

    assert os.path.exists(os.path.join(output_dir, "trace.json"))
    assert os.path.exists(os.path.join(output_dir, "statistics.json"))
    assert os.path.exists(os.path.join(output_dir, "artifacts", "dummy_ir.json"))

    with open(os.path.join(output_dir, "trace.json")) as f:
        data = json.load(f)
        assert len(data["events"]) == 1

    shutil.rmtree(output_dir)
