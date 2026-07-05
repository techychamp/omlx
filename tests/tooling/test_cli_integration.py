import pytest
import subprocess
import json

def test_cli_replay_mock():
    res = subprocess.run(["python", "omlx/tooling/cli/main.py", "replay", "dummy.json"], capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["status"] == "replaying session"
    assert data["file"] == "dummy.json"

def test_cli_summarize_mock():
    res = subprocess.run(["python", "omlx/tooling/cli/main.py", "summarize", "dummy.json"], capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["status"] == "summarizing"
    assert data["file"] == "dummy.json"
