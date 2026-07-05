from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
import asyncio
from omlx.planner.compiler.engine import CompilerEngine
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.compiler.backend.registry import AdapterRegistry
from omlx.api.v1.exceptions import CompilerError
import logging

logger = logging.getLogger("omlx.api.v1.compiler")

class CompilerArtifactSummary(BaseModel):
    node_count: int = 0
    root_count: int = 0
    has_translation: bool = False
    target_backend: str

class CompilerResult(BaseModel):
    success: bool = True
    artifacts: CompilerArtifactSummary
    diagnostics: Dict[str, str] = Field(default_factory=dict)

class CompilerRequest(BaseModel):
    model_id: str
    target_backend: str = "mlx"
    optimizations: Dict[str, bool] = Field(default_factory=dict)
    logical_ir: Optional[Any] = None

class Compiler:
    def __init__(self):
        self._engine = CompilerEngine()
        self._adapter_registry = AdapterRegistry()

    async def compile_async(self, request: CompilerRequest) -> CompilerResult:
        return await asyncio.to_thread(self.compile, request)

    def compile(self, request: CompilerRequest) -> CompilerResult:
        try:
            logger.info(f"Compiling model: {request.model_id}")
            ir = request.logical_ir if request.logical_ir else ExecutionIR(nodes={}, roots=[])
            physical_ir = self._engine.compile(ir)

            summary = CompilerArtifactSummary(
                node_count=len(physical_ir.nodes) if hasattr(physical_ir, 'nodes') else 0,
                root_count=len(physical_ir.roots) if hasattr(physical_ir, 'roots') else 0,
                target_backend=request.target_backend
            )

            if self._adapter_registry.exists(request.target_backend, "any", "autoregressive", "standard"):
                adapter = self._adapter_registry.resolve(request.target_backend, "any", "autoregressive", "standard")
                result = self._engine.translate(physical_ir, adapter)
                summary.has_translation = result is not None

            return CompilerResult(success=True, artifacts=summary)
        except Exception as e:
            raise CompilerError(f"Compilation failed: {str(e)}") from e

class CompilerRequestBuilder:
    def __init__(self):
        self._model_id: Optional[str] = None
        self._target_backend: str = "mlx"
        self._optimizations: Dict[str, bool] = {}
        self._logical_ir = None

    def with_model(self, model_id: str) -> 'CompilerRequestBuilder':
        self._model_id = model_id
        return self

    def with_backend(self, backend: str) -> 'CompilerRequestBuilder':
        self._target_backend = backend
        return self

    def enable_optimization(self, optimization: str) -> 'CompilerRequestBuilder':
        self._optimizations[optimization] = True
        return self

    def with_logical_ir(self, logical_ir: Any) -> 'CompilerRequestBuilder':
        self._logical_ir = logical_ir
        return self

    def build_request(self) -> CompilerRequest:
        if not self._model_id:
            raise ValueError("model_id is required")
        return CompilerRequest(
            model_id=self._model_id,
            target_backend=self._target_backend,
            optimizations=self._optimizations,
            logical_ir=self._logical_ir
        )

    def build(self) -> Compiler:
        return Compiler()
