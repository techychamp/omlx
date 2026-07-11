# SPDX-License-Identifier: Apache-2.0
"""
Runtime Compiler Service implementation.
Provides a first-class Runtime service for compiler orchestration.
"""

from typing import Any, Optional
import time
import logging
from dataclasses import dataclass

from omlx.planner.compiler.backend.adapter import TranslationResult
from omlx.runtime.compiler_integration import CompilerPipelineRunner

logger = logging.getLogger("omlx.compiler_service")


@dataclass(frozen=True)
class CompilerSession:
    """Immutable session tracking the lifecycle of a compiler invocation."""
    model_id: str
    start_time: float
    end_time: Optional[float] = None
    translation_result: Optional[TranslationResult] = None
    cache_plan: Optional[Any] = None
    diagnostics: list[str] = None
    status: str = "active"


class RuntimeCompilerService:
    """
    Service responsible for orchestrating the compiler pipeline.
    Owned exclusively by the Runtime instance and survives multiple requests.
    """

    def __init__(self, runtime: Any):
        """
        Initialize the compiler service with the parent Runtime.
        """
        self.runtime = runtime
        self._runner = CompilerPipelineRunner(runtime)
        self._statistics = {
            "total_compilations": 0,
            "successful_compilations": 0,
            "failed_compilations": 0,
            "total_compilation_time_ms": 0.0
        }
        self._diagnostics = []

    @property
    def runner(self) -> CompilerPipelineRunner:
        """Access the underlying pipeline runner."""
        return self._runner

    @property
    def statistics(self) -> dict:
        """Get current compiler statistics."""
        return dict(self._statistics)

    def run_compilation(self, model_id: str, request_context: Any = None) -> Optional[TranslationResult]:
        """
        Execute the compilation pipeline for a model and update statistics.
        Populates RuntimeContext automatically via the runner.
        """
        start_time = time.time()
        self._statistics["total_compilations"] += 1

        try:
            result = self._runner.run_pipeline(model_id, request_context)

            elapsed_ms = (time.time() - start_time) * 1000
            self._statistics["total_compilation_time_ms"] += elapsed_ms

            if result is not None:
                self._statistics["successful_compilations"] += 1
                status = "success"
            else:
                self._statistics["failed_compilations"] += 1
                status = "failed"

            session = CompilerSession(
                model_id=model_id,
                start_time=start_time,
                end_time=time.time(),
                translation_result=result,
                diagnostics=list(self._diagnostics),
                status=status
            )

            if self.runtime.feature_flags.COMPILER_CONTEXT_ENABLED:
                self.runtime.update_context(
                    compiler_session=session,
                    compiler_statistics=self.statistics
                )

            return result

        except Exception as e:
            self._statistics["failed_compilations"] += 1
            logger.error(f"Compilation pipeline failed: {e}", exc_info=True)
            return None
