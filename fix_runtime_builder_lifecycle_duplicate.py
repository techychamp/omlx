with open("omlx/runtime/builder.py", "r") as f:
    content = f.read()

# Fix the unresolved `adapter` variable error in the second block
# The second block is a fallback from previous modifications that lacks the adapter assignment
content = content.replace(
    """                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=adapter,
                    cache_plan=cache_plan,
                    cache_session=cache_session
                )""",
    """                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=None, # Fallback path has no adapter configured previously in the script
                    cache_plan=cache_plan,
                    cache_session=cache_session
                )"""
)

with open("omlx/runtime/builder.py", "w") as f:
    f.write(content)
