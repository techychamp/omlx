import pytest
from omlx.api.v1 import (
    RuntimeBuilder, RuntimeService,
    CompilerRequestBuilder, CompilerService, CompilerRequest,
    PlanningRequestBuilder, Planner, PlanningRequest,
    BackendRequestBuilder, BackendManager, BackendRequest,
    VerificationRequestBuilder, Verifier, VerificationRequest,
    Inspector,
    PluginManager,
    PerformanceMonitor,
    DiagnosticsRunner,
    ToolingManager
)

def test_runtime_builder():
    builder = RuntimeBuilder()
    runtime = builder.configure({"test": "value"}).enable("SOME_FEATURE").build()
    assert isinstance(runtime, RuntimeService)
    assert runtime.status == "bootstrapping"

def test_compiler_builder():
    builder = CompilerRequestBuilder()
    request = builder.with_model("test-model").with_backend("mlx").build_request()
    assert request.model_id == "test-model"
    assert request.target_backend == "mlx"

    compiler = builder.build()
    result = compiler.compile(request)
    assert result.success

@pytest.mark.asyncio
async def test_compiler_async():
    builder = CompilerRequestBuilder()
    request = builder.with_model("test-model").build_request()
    compiler = builder.build()
    result = await compiler.compile_async(request)
    assert result.success

def test_planning_builder():
    builder = PlanningRequestBuilder()
    request = builder.require_capability("attention").with_constraint("max_memory", 1024).build_request()
    assert "attention" in request.capabilities

    planner = builder.build()
    result = planner.plan(request)
    assert result.success

def test_backend_builder():
    builder = BackendRequestBuilder()
    request = builder.with_model_family("llama").build_request()

    manager = builder.build()
    result = manager.select_backend(request)
    assert result.selected_backend == "mlx"

def test_verification_builder():
    builder = VerificationRequestBuilder()
    request = builder.with_target("plan-123").build_request()

    verifier = builder.build()
    result = verifier.verify(request)
    assert result.passed

def test_inspector():
    inspector = Inspector()
    result = inspector.inspect("runtime")
    assert result.health_status == "healthy"

def test_plugin_manager():
    manager = PluginManager()
    result = manager.load_plugin("test-plugin")
    assert result.success

def test_performance_monitor():
    monitor = PerformanceMonitor()
    result = monitor.measure("engine")
    assert isinstance(result.metrics, list)

def test_diagnostics_runner():
    runner = DiagnosticsRunner()
    result = runner.run_diagnostics()
    assert result.issues_found == 0

def test_tooling_manager():
    manager = ToolingManager()
    result = manager.execute_tool("export_graph")
    assert result.success
