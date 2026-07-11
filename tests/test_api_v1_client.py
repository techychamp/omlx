import pytest
import asyncio
from omlx.api.v1.client import OMLXClient
from omlx.api.v1.generation import GenerateRequest, StreamRequest
from omlx.api.v1.runtime import RuntimeConfig
from omlx.api.v1.exceptions import ConfigurationError, OMLXRuntimeError

class MockGenerationService:
    def generate(self, request):
        from omlx.api.v1.generation import GenerateResponse
        return GenerateResponse(text="test response", finish_reason="stop", tokens_generated=2)

    async def stream(self, request):
        from omlx.api.v1.generation import StreamResponse
        yield StreamResponse(text_chunk="test ", is_finished=False)
        yield StreamResponse(text_chunk="response", is_finished=True)

class MockRuntimeService:
    def __init__(self):
        self.generation = MockGenerationService()

    def get_tooling(self):
        return {"tooling": "mock_tooling"}

@pytest.fixture
def client():
    runtime = MockRuntimeService()
    return OMLXClient(runtime)

def test_session_lifecycle(client):
    session = client.create_session({"context": "test"})
    assert session.session_id is not None
    assert session.metadata["context"] == "test"
    assert session.active is True

    fetched_session = client.get_session(session.session_id)
    assert fetched_session is session

    client.cancel_session(session.session_id)
    assert client.get_session(session.session_id).active is False

    client.cleanup_session(session.session_id)
    assert client.get_session(session.session_id) is None

def test_generate_sync(client):
    req = GenerateRequest(model_id="test-model", prompt="Hello")
    res = client.generate(req)
    assert res.text == "test response"

def test_generate_sync_invalid_session(client):
    req = GenerateRequest(model_id="test-model", prompt="Hello")
    with pytest.raises(ConfigurationError):
        client.generate(req, session_id="invalid-id")

@pytest.mark.asyncio
async def test_generate_async(client):
    req = GenerateRequest(model_id="test-model", prompt="Hello")
    res = await client.generate_async(req)
    assert res.text == "test response"

@pytest.mark.asyncio
async def test_stream_async(client):
    req = StreamRequest(model_id="test-model", prompt="Hello")
    chunks = []
    async for chunk in client.stream(req):
        chunks.append(chunk)
    assert len(chunks) == 2
    assert chunks[0].text_chunk == "test "
    assert chunks[1].text_chunk == "response"

@pytest.mark.asyncio
async def test_stream_async_invalid_session(client):
    req = StreamRequest(model_id="test-model", prompt="Hello")
    with pytest.raises(ConfigurationError):
        async for _ in client.stream(req, session_id="invalid-id"):
            pass

def test_config_profiles(client):
    config = RuntimeConfig(settings={"backend": "test"})
    client.apply_profile("test-profile", config)

    fetched_config = client.get_profile("test-profile")
    assert fetched_config is config
    assert fetched_config.settings["backend"] == "test"

def test_mock_integrations(client):
    assert client.get_tooling() == {"tooling": "mock_tooling"}
    with pytest.raises(OMLXRuntimeError):
         client.get_plugins()
