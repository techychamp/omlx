import pytest
from omlx.api.v1.client import OMLXClient
from omlx.workbench import DeveloperWorkbench
from omlx.workbench.navigation import WorkbenchModule, ModuleInfo

class MockRuntime:
    class _models:
        @staticmethod
        def get_info():
            return {"models": []}
    models = _models()

@pytest.fixture
def workbench():
    client = OMLXClient(runtime=MockRuntime())
    return DeveloperWorkbench(client)

def test_workbench_initialization(workbench):
    assert len(workbench.navigation.list_modules()) == 8
    assert workbench.navigation.get_module("dashboard") is not None

def test_dashboard_module(workbench):
    data = workbench.get_module_data("dashboard")
    assert "active_sessions" in data
    assert data["status"] == "Online"

def test_navigation_registration(workbench):
    custom_module = WorkbenchModule(ModuleInfo(id="custom", name="Custom", description="Test", route="/custom"))
    workbench.navigation.register_module(custom_module)
    assert workbench.navigation.get_module("custom") is not None

def test_module_data_retrieval(workbench):
    data = workbench.get_module_data("runtime_explorer")
    assert "sessions" in data

    data = workbench.get_module_data("model_explorer")
    assert "models" in data

def test_invalid_module(workbench):
    with pytest.raises(ValueError):
        workbench.get_module_data("invalid_module")
