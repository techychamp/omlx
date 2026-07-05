from omlx.runtime.compiler_integration import CompilerPipelineRunner
import sys
import unittest.mock as mock
import pytest

mock_mlx = mock.MagicMock()
mock_mlx.__version__ = "0.15.0"
sys.modules['mlx'] = mock_mlx
sys.modules['mlx.core'] = mock_mlx
sys.modules['mlx.core.metal'] = mock_mlx
sys.modules['mlx.nn'] = mock_mlx
sys.modules['mlx.utils'] = mock_mlx

mock_mlx_lm = mock.MagicMock()
sys.modules['mlx_lm'] = mock_mlx_lm
sys.modules['mlx_lm.generate'] = mock_mlx_lm
sys.modules['mlx_lm.models'] = mock_mlx_lm
sys.modules['mlx_lm.models.cache'] = mock_mlx_lm
sys.modules['mlx_lm.sample_utils'] = mock_mlx_lm
sys.modules['mlx_vlm'] = mock_mlx_lm
sys.modules['mlx_vlm.speculative'] = mock_mlx_lm
sys.modules['mlx_vlm.speculative.utils'] = mock_mlx_lm

sys.modules['numpy'] = mock.MagicMock()
class MockBaseModel:
    pass
class MockPydantic(mock.MagicMock):
    __path__ = []
    BaseModel = MockBaseModel
    Field = lambda *args, **kwargs: None
sys.modules['pydantic'] = MockPydantic()
sys.modules['fastapi'] = mock.MagicMock()
sys.modules['fastapi.security'] = mock.MagicMock()
sys.modules['fastapi.responses'] = mock.MagicMock()
sys.modules['sse_starlette'] = mock.MagicMock()
sys.modules['sse_starlette.sse'] = mock.MagicMock()
sys.modules['starlette'] = mock.MagicMock()
sys.modules['starlette.background'] = mock.MagicMock()
sys.modules['regex'] = mock.MagicMock()
sys.modules['jsonschema'] = mock.MagicMock()
sys.modules['openai_harmony'] = mock.MagicMock()
sys.modules['PIL'] = mock.MagicMock()
sys.modules['itsdangerous'] = mock.MagicMock()
sys.modules['requests'] = mock.MagicMock()
sys.modules['fastapi.templating'] = mock.MagicMock()
class MockBaseModel:
    pass
class MockPydantic(mock.MagicMock):
    __path__ = []
    BaseModel = MockBaseModel
    Field = lambda *args, **kwargs: None
sys.modules['pydantic'] = MockPydantic()
sys.modules['fastapi'] = mock.MagicMock()
sys.modules['fastapi.security'] = mock.MagicMock()
sys.modules['fastapi.responses'] = mock.MagicMock()
sys.modules['sse_starlette'] = mock.MagicMock()
sys.modules['sse_starlette.sse'] = mock.MagicMock()
sys.modules['starlette'] = mock.MagicMock()
sys.modules['starlette.background'] = mock.MagicMock()
sys.modules['regex'] = mock.MagicMock()
sys.modules['jsonschema'] = mock.MagicMock()
sys.modules['openai_harmony'] = mock.MagicMock()
sys.modules['PIL'] = mock.MagicMock()
sys.modules['itsdangerous'] = mock.MagicMock()
sys.modules['requests'] = mock.MagicMock()
sys.modules['fastapi.templating'] = mock.MagicMock()
class MockBaseModel:
    pass
class MockPydantic(mock.MagicMock):
    __path__ = []
    BaseModel = MockBaseModel
    Field = lambda *args, **kwargs: None
sys.modules['pydantic'] = MockPydantic()
sys.modules['fastapi'] = mock.MagicMock()
sys.modules['fastapi.security'] = mock.MagicMock()
sys.modules['fastapi.responses'] = mock.MagicMock()
sys.modules['sse_starlette'] = mock.MagicMock()
sys.modules['sse_starlette.sse'] = mock.MagicMock()
sys.modules['starlette'] = mock.MagicMock()
sys.modules['starlette.background'] = mock.MagicMock()
sys.modules['regex'] = mock.MagicMock()
sys.modules['jsonschema'] = mock.MagicMock()
sys.modules['openai_harmony'] = mock.MagicMock()
sys.modules['PIL'] = mock.MagicMock()
sys.modules['itsdangerous'] = mock.MagicMock()
sys.modules['requests'] = mock.MagicMock()
sys.modules['fastapi.templating'] = mock.MagicMock()
sys.modules['huggingface_hub'] = mock.MagicMock()

from omlx.runtime.feature_flags import FeatureFlags
from omlx.runtime.builder import RuntimeBuilder, RuntimeStateEnum
from omlx.engine_pool import EnginePool
from omlx.engine_core import EngineConfig
from omlx.engine_core import EngineCore
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.planner.planner import ExecutionPlan

class MockModel:
    language_model = None

class MockTokenizer:
    def encode(self, *args, **kwargs):
        return []
    @property
    def eos_token_id(self):
        return 2
    @property
    def pad_token_id(self):
        return 0
    @property
    def bos_token_id(self):
        return 1


def test_compiler_runtime_integration():
    flags = FeatureFlags(
        COMPILER_RUNTIME_PIPELINE_ENABLED=True,
        COMPILER_RUNTIME_ENABLED=True,
        COMPILER_CONTEXT_ENABLED=True,
        CAPABILITY_RUNTIME_ENABLED=True,
        PLANNER_RUNTIME_ENABLED=True,
        LOWERING_RUNTIME_ENABLED=True,
        ADAPTER_RUNTIME_ENABLED=True,
        EXECUTION_PLAN_RUNTIME_ENABLED=True,
        EXECUTION_PROFILE_COMPATIBILITY_ENABLED=True,
        LEGACY_RUNTIME_ENABLED=True
    )

    with mock.patch("omlx.capabilities.resolver.CapabilityResolver.resolve") as mock_resolve:
        mock_resolve.return_value = CapabilityDescriptor(execution_family=ExecutionFamily.AUTOREGRESSIVE)
        builder = RuntimeBuilder().with_feature_flags(flags)
        runtime = builder.build()

        # Test compiler pipeline execution directly through Runtime, without EnginePool
        runner = CompilerPipelineRunner(runtime)

        with mock.patch("omlx.planner.compiler.backend.registry.AdapterRegistry.resolve") as mock_get_adapter:
            mock_adapter = mock.MagicMock()
            mock_translation = mock.MagicMock()
            mock_translation.backend_operation_graph = "mock_graph"
            mock_adapter.translate.return_value = mock_translation
            mock_get_adapter.return_value = mock_adapter

            result = runner.run_pipeline("mock-model")

            # Assertions
            assert result is not None
            assert runtime.context.capability_descriptor is not None
            assert runtime.context.execution_plan is not None
            assert runtime.context.translation_result is not None
            assert runtime.context.backend_operation_graph == "mock_graph"
