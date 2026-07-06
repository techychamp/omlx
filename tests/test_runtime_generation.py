import pytest
from unittest.mock import MagicMock
from omlx.runtime.builder import RuntimeBuilder
from omlx.runtime.builder import RuntimeContext

class MockTranslationResult:
    def __init__(self):
        self.backend_operation_graph = MagicMock()
        self.backend_descriptor = MagicMock(backend_id="mlx")

class MockAdapter:
    def execute(self, op, ctx):
        import mlx.core as mx
        return {"result": {"logits": mx.array([[[1.0, 0.0]]])}}

def test_runtime_generation_short():
    builder = RuntimeBuilder()
    runtime = builder.build()

    runtime._compile_request = MagicMock(return_value=MockTranslationResult())
    runtime._resolve_adapter = MagicMock(return_value=MockAdapter())
    runtime.streaming_controller = MagicMock()
    runtime.streaming_controller.create_session.return_value = MagicMock(session_id="test_sess")

    req_ctx = MagicMock()
    req_ctx.model = "test_model"
    req_ctx.prompt = "test_prompt"
    req_ctx.tokenizer = MagicMock()
    req_ctx.tokenizer.encode.return_value = [1]
    req_ctx.tokenizer.decode.return_value = " token"
    req_ctx.tokenizer.eos_token_id = 999

    mock_exec_res = MagicMock()
    mock_exec_res.status.value = "success"
    mock_exec_res.model_output = {"last_output": {"result": {"logits": "simulated_logits"}}}
    runtime._execute_forward_pass = MagicMock(return_value=mock_exec_res)

    res = runtime.generate(req_ctx, max_tokens=3)

    assert len(res["tokens"]) == 3
    assert runtime._execute_forward_pass.call_count == 3
    assert "session" in res

def test_runtime_generation_eos():
    builder = RuntimeBuilder()
    runtime = builder.build()

    runtime._compile_request = MagicMock(return_value=MockTranslationResult())
    runtime._resolve_adapter = MagicMock(return_value=MockAdapter())
    runtime.streaming_controller = MagicMock()
    runtime.streaming_controller.create_session.return_value = MagicMock(session_id="test_sess")

    req_ctx = MagicMock()
    req_ctx.model = "test_model"
    req_ctx.prompt = "test_prompt"
    req_ctx.tokenizer = MagicMock()
    req_ctx.tokenizer.encode.return_value = [1]
    req_ctx.tokenizer.decode.return_value = " token"
    req_ctx.tokenizer.eos_token_id = 999

    mock_exec_res = MagicMock()
    mock_exec_res.status.value = "success"
    mock_exec_res.model_output = {"last_output": {"result": {"logits": "simulated_logits"}}}
    runtime._execute_forward_pass = MagicMock(return_value=mock_exec_res)

    runtime._sample_token = MagicMock(side_effect=[(10, " ten"), (999, " eos")])

    res = runtime.generate(req_ctx, max_tokens=5)

    assert len(res["tokens"]) == 2
    assert runtime._execute_forward_pass.call_count == 2

def test_runtime_generation_stop_sequence():
    builder = RuntimeBuilder()
    runtime = builder.build()

    runtime._compile_request = MagicMock(return_value=MockTranslationResult())
    runtime._resolve_adapter = MagicMock(return_value=MockAdapter())
    runtime.streaming_controller = MagicMock()
    runtime.streaming_controller.create_session.return_value = MagicMock(session_id="test_sess")

    req_ctx = MagicMock()
    req_ctx.model = "test_model"
    req_ctx.prompt = "test_prompt"
    req_ctx.tokenizer = MagicMock()
    req_ctx.tokenizer.encode.return_value = [1]
    req_ctx.tokenizer.decode.return_value = " token"

    mock_exec_res = MagicMock()
    mock_exec_res.status.value = "success"
    mock_exec_res.model_output = {"last_output": {"result": {"logits": "simulated_logits"}}}
    runtime._execute_forward_pass = MagicMock(return_value=mock_exec_res)

    runtime._sample_token = MagicMock(side_effect=[(10, " hello"), (11, " world")])

    res = runtime.generate(req_ctx, max_tokens=5, stop_sequences=["world"])

    assert len(res["tokens"]) == 2
    assert res["generated_text"] == " hello world"
