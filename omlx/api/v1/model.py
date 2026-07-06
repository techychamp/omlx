from typing import List, Optional, Any
from pydantic import BaseModel, Field
from omlx.api.v1.exceptions import ConfigurationError

class ModelDescriptor(BaseModel):
    model_config = {'frozen': True}
    model_id: str
    architecture: str
    parameters_billions: float
    quantization: str

class ModelInfo(BaseModel):
    model_config = {'frozen': True}
    descriptor: ModelDescriptor
    is_loaded: bool
    memory_usage_mb: float

class ModelLoadBuilder:
    def __init__(self):
        self._model_id = None
        self._backend = "mlx"

    def with_model_id(self, model_id: str) -> 'ModelLoadBuilder':
        self._model_id = model_id
        return self

    def with_backend(self, backend: str) -> 'ModelLoadBuilder':
        self._backend = backend
        return self

    def build(self) -> dict:
        return {"model_id": self._model_id, "backend": self._backend}

class ModelService:
    def __init__(self, internal_runtime: Any):
        self._runtime = internal_runtime

    def load_model(self, request: dict) -> bool:
        if hasattr(self._runtime, "engine_pool") and self._runtime.engine_pool:
            if hasattr(self._runtime.engine_pool, "load"):
                return self._runtime.engine_pool.load(request["model_id"])
        raise NotImplementedError("Engine pool model loading is not currently implemented in this context")

    def unload_model(self, model_id: str) -> bool:
        if hasattr(self._runtime, "engine_pool") and self._runtime.engine_pool:
            if hasattr(self._runtime.engine_pool, "unload"):
                return self._runtime.engine_pool.unload(model_id)
        raise NotImplementedError("Engine pool model unloading is not currently implemented in this context")

    def list_models(self) -> List[ModelInfo]:
        if hasattr(self._runtime, "engine_pool") and self._runtime.engine_pool:
             if hasattr(self._runtime.engine_pool, "list_models"):
                 return [
                     ModelInfo(
                         descriptor=ModelDescriptor(
                             model_id=m,
                             architecture="llama", # Future: extract from actual descriptor
                             parameters_billions=7.0,
                             quantization="awq"
                         ),
                         is_loaded=True,
                         memory_usage_mb=0
                     ) for m in self._runtime.engine_pool.list_models()
                 ]
        raise NotImplementedError("Engine pool model listing is not currently implemented in this context")

    def model_information(self, model_id: str) -> Optional[ModelInfo]:
        raise NotImplementedError("Detailed model information retrieval is not implemented yet")
