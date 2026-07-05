import pytest
from omlx.runtime.builder import RuntimeBuilder
from omlx.runtime.compiler_service import RuntimeCompilerService
from omlx.runtime.feature_flags import FeatureFlags

def test_compiler_service_initialization():
    builder = RuntimeBuilder()
    runtime = builder.build()

    assert hasattr(runtime, "compiler_service")
    assert isinstance(runtime.compiler_service, RuntimeCompilerService)
    assert runtime.compiler_service.runtime is runtime

def test_compiler_service_statistics():
    builder = RuntimeBuilder()
    runtime = builder.build()

    stats = runtime.compiler_service.statistics
    assert stats["total_compilations"] == 0
    assert stats["successful_compilations"] == 0
    assert stats["failed_compilations"] == 0
