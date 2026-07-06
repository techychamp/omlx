
import os
import pytest
from omlx.runtime.observability import Observer, BundleExporter

def test_bundle_export(tmp_path):
    obs = Observer()
    obs.track_artifact("test_artifact", {"data": 123})

    output_dir = tmp_path / "export"
    BundleExporter.export(obs, str(output_dir))

    assert os.path.exists(output_dir / "trace.json")
    assert os.path.exists(output_dir / "timeline.json")
    assert os.path.exists(output_dir / "statistics.json")
    assert os.path.exists(output_dir / "artifacts" / "test_artifact.json")

def test_bundle_export_session(tmp_path):
    obs = Observer()
    obs.track_artifact("test_artifact", {"data": 123})

    session = obs.build_session(
        end_time=0.0,
        status="success",
        generated_tokens=[],
        statistics={}
    )

    output_dir = tmp_path / "export_session"
    BundleExporter.export(session, str(output_dir))

    assert os.path.exists(output_dir / "trace.json")
    assert os.path.exists(output_dir / "timeline.json")
    assert os.path.exists(output_dir / "statistics.json")
    assert os.path.exists(output_dir / "artifacts" / "test_artifact.json")
