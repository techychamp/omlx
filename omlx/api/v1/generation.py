from typing import List, Optional, AsyncGenerator, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
import asyncio
from omlx.api.v1.exceptions import ConfigurationError

class GenerateRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    model_id: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

class GenerateResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    text: str
    finish_reason: str
    tokens_generated: int

class StreamRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    model_id: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

class StreamResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    text_chunk: str
    is_finished: bool

class GenerateRequestBuilder:
    def __init__(self):
        self._model_id = ""
        self._prompt = ""
        self._max_tokens = 100

    def with_model(self, model_id: str) -> 'GenerateRequestBuilder':
        self._model_id = model_id
        return self

    def with_prompt(self, prompt: str) -> 'GenerateRequestBuilder':
        self._prompt = prompt
        return self

    def build(self) -> GenerateRequest:
        return GenerateRequest(model_id=self._model_id, prompt=self._prompt, max_tokens=self._max_tokens)

class StreamRequestBuilder:
    def __init__(self):
        self._model_id = ""
        self._prompt = ""

    def with_model(self, model_id: str) -> 'StreamRequestBuilder':
        self._model_id = model_id
        return self

    def with_prompt(self, prompt: str) -> 'StreamRequestBuilder':
        self._prompt = prompt
        return self

    def build(self) -> StreamRequest:
        return StreamRequest(model_id=self._model_id, prompt=self._prompt)


class RuntimeRequest:
    """Stable runtime request object replacing ad-hoc shims."""
    def __init__(self, model: str, prompt: str):
        self.model = model
        self.prompt = prompt

class GenerationService:
    def __init__(self, internal_runtime: Any):
        self._runtime = internal_runtime

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        req = RuntimeRequest(model=request.model_id, prompt=request.prompt)
        res = self._runtime.generate(
            request_context=req,
            max_tokens=request.max_tokens,
            sampler=request.temperature
        )
        return GenerateResponse(
            text=res.get("generated_text", ""),
            finish_reason="stop",
            tokens_generated=len(res.get("tokens", []))
        )

    async def stream(self, request: StreamRequest) -> AsyncGenerator[StreamResponse, None]:
        req = RuntimeRequest(model=request.model_id, prompt=request.prompt)
        res = await asyncio.to_thread(self._runtime.generate, request_context=req, max_tokens=request.max_tokens, sampler=request.temperature)
        yield StreamResponse(text_chunk=res.get("generated_text", ""), is_finished=True)

    def batch_generate(self, requests: List[GenerateRequest]) -> List[GenerateResponse]:
        return [self.generate(r) for r in requests]
