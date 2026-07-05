with open("omlx/optimization/pipeline.py", "r") as f:
    content = f.read()

content = content.replace("from .passes import CompilerStage, OptimizationContext, PassCategory", "from .passes import CompilerStage, OptimizationContext, PassCategory, AnalysisPass\nimport concurrent.futures")

execution_loop = """
        def execute_pass(p, art, ctx):
            start_time = time.perf_counter()
            success = False
            result_art = art
            if ctx.tracker:
                 ctx.tracker.add_diagnostic(
                     DiagnosticLevel.INFO,
                     f"Executing pass '{p.name}'.",
                     pass_name=p.name
                 )
            try:
                result_art = p.apply(art, ctx)
                success = True
            except Exception as e:
                if ctx.tracker:
                    ctx.tracker.add_diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Pass '{p.name}' failed with exception: {e}",
                        pass_name=p.name
                    )
                raise e # Fail-fast for now
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
                    idx = next_idx
                    continue

            # Execute single pass
            current_artifact = execute_pass(p, current_artifact, context)
            idx += 1"""

content = content.replace("""        for p in ordered_passes:

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
                    )""", execution_loop)

with open("omlx/optimization/pipeline.py", "w") as f:
    f.write(content)
