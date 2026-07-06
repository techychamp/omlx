from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import asyncio
from omlx.api.v1.exceptions import CompilerError
from omlx.api.v1.generation import RuntimeRequest
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

class CompilerService:
    def __init__(self, internal_runtime: Any = None):
        self._runtime = internal_runtime
        if self._runtime and hasattr(self._runtime, "compiler_service"):
             self._internal_compiler = self._runtime.compiler_service
        else:
             from omlx.planner.compiler.engine import CompilerEngine
             from omlx.planner.compiler.backend.registry import AdapterRegistry
             self._engine = CompilerEngine()
             self._adapter_registry = AdapterRegistry()
             self._internal_compiler = None

    async def compile_async(self, request: CompilerRequest) -> CompilerResult:
        return await asyncio.to_thread(self.compile, request)

    def compile(self, request: CompilerRequest) -> CompilerResult:
        try:
            logger.info(f"Compiling model: {request.model_id}")

            # Delegate to runtime compiler service if available
            if self._internal_compiler:
                req = RuntimeRequest(model=request.model_id, prompt="")
                res = self._internal_compiler.run_compilation(request.model_id, req)

                node_count = 0
                has_translation = False
                if res:
                    has_translation = True
                    backend_graph = getattr(res, "backend_graph", getattr(res, "backend_operation_graph", None))
                    if backend_graph and hasattr(backend_graph, "nodes"):
                        node_count = len(backend_graph.nodes)

                return CompilerResult(
                    success=True,
                    artifacts=CompilerArtifactSummary(
                        node_count=node_count,
                        target_backend=request.target_backend,
                        has_translation=has_translation
                    )
                )

            # Fallback path if instantiated outside runtime
            from omlx.planner.ir.graph import ExecutionIR
            ir = ExecutionIR(nodes={}, roots=[])
            physical_ir = self._engine.compile(ir)

            summary_args = {
                "node_count": len(physical_ir.nodes) if hasattr(physical_ir, 'nodes') else 0,
                "root_count": len(physical_ir.roots) if hasattr(physical_ir, 'roots') else 0,
                "target_backend": request.target_backend,
                "has_translation": False
            }

            if self._adapter_registry.exists(request.target_backend, "any", "autoregressive", "standard"):
                adapter = self._adapter_registry.resolve(request.target_backend, "any", "autoregressive", "standard")
                result = self._engine.translate(physical_ir, adapter)
                if result is not None:
                    summary_args["has_translation"] = True

            return CompilerResult(
                success=True,
                artifacts=CompilerArtifactSummary(**summary_args)
            )
        except Exception as e:
            raise CompilerError(f"Compilation failed: {str(e)}") from e

class CompilerRequestBuilder:
    def __init__(self):
        self._model_id: Optional[str] = None
        self._target_backend: str = "mlx"
        self._optimizations: Dict[str, bool] = {}

    def with_model(self, model_id: str) -> 'CompilerRequestBuilder':
        self._model_id = model_id
        return self

    def with_backend(self, backend: str) -> 'CompilerRequestBuilder':
        self._target_backend = backend
        return self

    def enable_optimization(self, optimization: str) -> 'CompilerRequestBuilder':
        self._optimizations[optimization] = True
        return self

    def build_request(self) -> CompilerRequest:
        if not self._model_id:
            raise ValueError("model_id is required")
        return CompilerRequest(
            model_id=self._model_id,
            target_backend=self._target_backend,
            optimizations=self._optimizations
        )

    def build(self) -> CompilerService:
        return CompilerService()
