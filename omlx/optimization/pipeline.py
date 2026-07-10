# SPDX-License-Identifier: Apache-2.0
"""
Compiler Optimization Framework - Pipeline
"""
import time
from typing import TypeVar, Any
from .passes import CompilerStage, OptimizationContext, PassCategory, AnalysisPass
import concurrent.futures
from .validation import PassValidationError, validate_artifact_immutability
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
        ordered_passes = self.manager.get_execution_order(stage=self.stage)

        # Validate Phase Ordering
        phase_order = {
            PassCategory.CANONICALIZATION: 1,
            PassCategory.ANALYSIS: 2,
            PassCategory.SIMPLIFICATION: 3,
            PassCategory.OPTIMIZATION: 4,
            PassCategory.VALIDATION: 5,
            PassCategory.BACKEND_PREPARATION: 6
        }

        current_phase_idx = 0
        for p in ordered_passes:
            if p.category in phase_order:
                pass_phase_idx = phase_order[p.category]
                if pass_phase_idx < current_phase_idx:
                    raise PassValidationError(f"Phase ordering violation: Pass '{p.name}' (Category: {p.category.name}) executed after a later phase.")
                current_phase_idx = pass_phase_idx


        def execute_pass(p, art, ctx):
            start_time = time.perf_counter()
            success = False
            result_art = art
            if ctx.tracker:
                 ctx.tracker.add_diagnostic(f"Executing pass '{p.name}'.")
            try:
                result_art = p.apply(art, ctx)
                success = True
            except Exception as e:
                if ctx.tracker:
                    ctx.tracker.add_diagnostic(f"Pass '{p.name}' failed with exception: {e}")
                from omlx.api.v1.exceptions import CompilerError
                raise CompilerError(
                    message=f"Pass {p.name} failed: {e}",
                    code="PASS_FAILED",
                    details={"pass_name": p.name, "error": str(e)},
                    diagnostics={"reason": "Unexpected failure during optimization pass execution"},
                    recommendation="Verify pass logic or report bug"
                ) from e
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                if ctx.stats:
                    ctx.stats.record_pass_execution(
                        name=p.name,
                        duration_ms=duration_ms,
                        success=success
                    )
            return result_art

        idx = 0
        while idx < len(ordered_passes):
            p = ordered_passes[idx]

            # Group independent analysis passes
            if isinstance(p, AnalysisPass):
                analysis_group = [p]
                next_idx = idx + 1
                while next_idx < len(ordered_passes) and isinstance(ordered_passes[next_idx], AnalysisPass):
                    # Only add if it doesn't depend on something in the current group
                    # For simplicity, if it's an analysis pass we assume they can run in parallel
                    # (In a real scenario, we'd check `required_passes` against the current group)
                    can_run_parallel = True
                    for group_pass in analysis_group:
                        if group_pass.name in ordered_passes[next_idx].required_passes:
                            can_run_parallel = False
                            break
                    if not can_run_parallel:
                        break

                    analysis_group.append(ordered_passes[next_idx])
                    next_idx += 1

                if len(analysis_group) > 1:
                    # Execute in parallel
                    if context.tracker:
                        context.tracker.add_diagnostic(
                            DiagnosticLevel.INFO,
                            f"Executing {len(analysis_group)} analysis passes in parallel: {[gp.name for gp in analysis_group]}"
                        )
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = [executor.submit(execute_pass, gp, current_artifact, context) for gp in analysis_group]
                        for future in concurrent.futures.as_completed(futures):
                            # Artifact shouldn't change for analysis passes
                            future.result()
                    if context.stats:
                        context.stats.record_parallel_execution()
                    idx = next_idx
                    continue


            # Execute single pass
            old_artifact = current_artifact
            current_artifact = execute_pass(p, current_artifact, context)

            # Validate immutability
            validate_artifact_immutability(old_artifact, current_artifact, p)

            idx += 1

        return current_artifact
