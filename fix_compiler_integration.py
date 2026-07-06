import re

with open("omlx/runtime/compiler_integration.py", "r") as f:
    content = f.read()

# Only keep the first definition of CompilerPipelineRunner to avoid duplicates
match = re.search(r'class CompilerPipelineRunner:.*?(?=\nclass CompilerPipelineRunner:)', content, re.DOTALL)
if match:
    # Just cut off at the second class CompilerPipelineRunner:
    first_part = content[:content.find("class CompilerPipelineRunner:", 20)]

    # Add cache planner to the run_pipeline method
    cache_planning_code = """
        # Cache Planning
        cache_plan = None
        if flags.CACHE_PLANNING_ENABLED:
            with get_observer().observe_phase("Compilation", "CachePlanner", "plan"):
                try:
                    from omlx.framework.cache.descriptor import CacheDescriptor
                    from omlx.planner.cache_planner import CachePlanner
                    cache_planner = CachePlanner(flags)

                    # Create a dummy cache descriptor for now or derive from execution plan
                    desc = CacheDescriptor(cache_type="paged", capacity=1024, element_size=8)
                    cache_plan = cache_planner.plan(desc)
                    if cache_plan:
                        get_observer().track_artifact("CachePlan", cache_plan)
                        logger.debug(f"Cache planning completed for {model_id}")
                except Exception as e:
                    logger.error(f"Cache planning failed: {e}", exc_info=True)
                    get_observer().add_diagnostic(f"Cache planning failed: {e}")
"""

    first_part = first_part.replace("if physical_ir is None:", f"if physical_ir is None:\n                return None\n{cache_planning_code}")

    # Update context update with cache_plan
    first_part = first_part.replace(
        "translation_result=translation_result,",
        "translation_result=translation_result,\n                    cache_plan=cache_plan,"
    )

    with open("omlx/runtime/compiler_integration.py", "w") as f:
        f.write(first_part)
