from types import SimpleNamespace

import pytest

from omlx.admin import routes as admin_routes
from omlx.settings import LoggingSettings


def test_available_log_files_includes_runtime_log(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "server.log").write_text("server\n", encoding="utf-8")
    (log_dir / "runtime.log").write_text("runtime\n", encoding="utf-8")
    (log_dir / "other.log").write_text("other\n", encoding="utf-8")

    files = admin_routes._get_available_log_files(log_dir)

    assert "server.log" in files
    assert "runtime.log" in files
    assert "other.log" not in files


@pytest.mark.asyncio
async def test_get_logs_defaults_to_runtime_when_server_log_empty(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "server.log").write_text("", encoding="utf-8")
    (log_dir / "runtime.log").write_text("server started\nrequest completed\n", encoding="utf-8")
    settings = SimpleNamespace(
        base_path=tmp_path,
        logging=LoggingSettings(log_dir=str(log_dir)),
    )
    monkeypatch.setattr(admin_routes, "_get_global_settings", lambda: settings)

    response = await admin_routes.get_logs(lines=100, file=None, is_admin=True)

    assert response["log_file"] == "runtime.log"
    assert "server started" in response["logs"]
    assert response["total_lines"] == 2
