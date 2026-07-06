import re

with open("omlx/runtime/builder.py", "r") as f:
    content = f.read()

replacement = """
                # Cache Session Lifecycle Coordination (Owned by Runtime)
                cache_session = None
                cache_plan = getattr(translation_result, "cache_plan", None)
                if cache_plan:
                    from omlx.runtime.execution.cache_session import CacheSession
                    cache_session = CacheSession(cache_plan)
                    cache_session.activate()
                    logger.debug(f"Runtime activated cache session for plan: {cache_plan.plan_id}")

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=adapter,
                    cache_plan=cache_plan,
                    cache_session=cache_session
                )

                execution_result = self.execution_engine.execute(exec_context)

                if cache_session:
                    cache_session.deactivate()
                    logger.debug("Runtime deactivated cache session")

                logger.debug(f"Execution Engine completed with status {execution_result.status}")

                return execution_result
"""

# Replace in execute_request
pattern = re.compile(
    r'# Construct ExecutionContext.*?return execution_result',
    re.DOTALL
)

if pattern.search(content):
    content = pattern.sub(replacement.strip(), content)
    with open("omlx/runtime/builder.py", "w") as f:
        f.write(content)
else:
    print("Could not find pattern in omlx/runtime/builder.py")
