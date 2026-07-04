# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Pipeline
"""
import time
from typing import TypeVar, Any
from .passes import CompilerStage, OptimizationContext
from .manager import PassManager
from .diagnostics import DiagnosticLevel

T = TypeVar("T")

class OptimizationPipeline:
    def __init__(self, stage: CompilerStage, manager: PassManager):
        self.stage = stage
        self.manager = manager

    def execute(self, artifact: T, context: OptimizationContext) -> T:
        """
        Executes the registered passes for the pipeline's stage on the artifact.
        Passes are executed in topological order.
        """
        current_artifact = artifact
        ordered_passes = self.manager.get_execution_order()

        for p in ordered_passes:
            if self.stage not in p.supported_stages:
                if context.tracker:
                     context.tracker.add_diagnostic(
                         DiagnosticLevel.INFO,
                         f"Skipped pass '{p.name}' because it does not support stage {self.stage.name}.",
                         pass_name=p.name
                     )
                continue

            start_time = time.perf_counter()
            success = False

            if context.tracker:
                 context.tracker.add_diagnostic(
                     DiagnosticLevel.INFO,
                     f"Executing pass '{p.name}'.",
                     pass_name=p.name
                 )

            try:
                # Apply the pass, creating a new artifact if it mutates
                current_artifact = p.apply(current_artifact, context)
                success = True
            except Exception as e:
                if context.tracker:
                    context.tracker.add_diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Pass '{p.name}' failed with exception: {e}",
                        pass_name=p.name
                    )
                raise e # Fail-fast for now
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                if context.stats:
                    context.stats.record_pass_execution(
                        name=p.name,
                        duration_ms=duration_ms,
                        success=success
                    )

        return current_artifact
