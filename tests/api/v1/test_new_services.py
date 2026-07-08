import pytest
import asyncio
from typing import Any
from omlx.api.v1 import (
    ModelService, ModelLoadBuilder, ModelDescriptor, ModelInfo,
    GenerationService, GenerateRequestBuilder, StreamRequestBuilder,
    StreamingService,
    ObservationService, ObservationQueryBuilder,
    QuantizationService, CapabilityService,
    CompilerService, CompilerRequestBuilder
)

class MockRuntime:
    def __init__(self):
        self.engine_pool = MockEnginePool()
        self.compiler_service = MockCompiler()

    def generate(self, request_context: Any, max_tokens: int, temperature: float) -> dict:
        return {
            "generated_text": "delegated text",
            "tokens": [1, 2, 3]
        }

class MockEnginePool:
    def load(self, model_id: str) -> bool:
        return True

    def unload(self, model_id: str) -> bool:
        return True

    def list_models(self) -> list:
        return ["model-a", "model-b"]

class MockCompiler:
    def run_compilation(self, model_id: str, request_context: Any) -> Any:
        class MockGraph:
            nodes = [1, 2]
        class MockRes:
            backend_graph = MockGraph()
        return MockRes()

def test_model_service_delegation():
    runtime = MockRuntime()
    service = ModelService(runtime)

    builder = ModelLoadBuilder()
    req = builder.with_model_id("test").build()

    assert service.load_model(req)
    assert service.unload_model("test")

    models = service.list_models()
    assert len(models) == 2
    assert models[0].descriptor.model_id == "model-a"

def test_generation_service_delegation():
    runtime = MockRuntime()
    service = GenerationService(runtime)

    builder = GenerateRequestBuilder()
    req = builder.with_model("test").with_prompt("hello").build()

    resp = service.generate(req)
    assert resp.text == "delegated text"
    assert resp.tokens_generated == 3

def test_compiler_service_delegation():
    runtime = MockRuntime()
    service = CompilerService(runtime)

    builder = CompilerRequestBuilder()
    req = builder.with_model("test").build_request()

    resp = service.compile(req)
    assert resp.artifacts.node_count == 2
    assert resp.artifacts.has_translation is True

def test_streaming_lifecycle():
    service = StreamingService()
    assert isinstance(service.stream_subscriptions(), list)
    assert service.stream_status("id") == "active"
    assert service.stream_lifecycle("id", "stop")

def test_observation_service():
    service = ObservationService()
    builder = ObservationQueryBuilder()
    req = builder.with_session("sess").build()

    assert isinstance(service.sessions(), list)
    assert isinstance(service.timeline("sess"), list)
    assert isinstance(service.statistics("sess"), dict)
    assert isinstance(service.diagnostics("sess"), dict)

def test_quantization_service():
    service = QuantizationService()
    info = service.get_info("test")
    assert info.method == "awq"

def test_capability_service():
    service = CapabilityService()
    caps = service.list_capabilities()
    assert len(caps) > 0
    assert caps[0].name == "attention"
