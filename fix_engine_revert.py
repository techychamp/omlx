with open("omlx/runtime/execution/engine.py", "r") as f:
    content = f.read()

replacement = """        with get_observer().observe_phase("Execution", "Engine", "execute"):
            try:
                # The execution engine purely consumes the context.
                # If cache is required, it accesses context.cache_session without managing its lifecycle.
                if getattr(context, "cache_session", None):
                    logger.debug(f"ExecutionEngine utilizing cache session for plan: {context.cache_session.cache_plan.plan_id}")

                result = self._executor.execute(context.backend_operation_graph, context)
                get_observer().track_artifact("ExecutionResult", result)
                return result"""

# Find the block to replace
start_idx = content.find('        with get_observer().observe_phase("Execution", "Engine", "execute"):')
end_idx = content.find('            except Exception as e:', start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + replacement + "\n" + content[end_idx:]
    with open("omlx/runtime/execution/engine.py", "w") as f:
        f.write(content)
else:
    print("Could not find the block to replace.")
