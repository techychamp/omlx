import re

with open("omlx/engine_core.py", "r") as f:
    content = f.read()

# Replace the capability and profile resolution block in engine_core.py
old_block = """            # 3. Build ExecutionContext and resolve profile / backend factory
            context = ExecutionContext(
                model_info=model_info,
                engine_capabilities=engine_caps,
                feature_flags=flags,
            )
            profile_registry = get_profile_registry()
            profile, backend_factory = profile_registry.resolve(context)"""

new_block = """            # 3. Build ExecutionContext and resolve profile / backend factory
            context = ExecutionContext(
                model_info=model_info,
                engine_capabilities=engine_caps,
                feature_flags=flags,
            )
            profile_registry = get_profile_registry()
            profile, backend_factory = profile_registry.resolve(context)

            # MIG-002: Check if execution plan routing is enabled
            if flags.EXECUTION_PLAN_RUNTIME_ENABLED or flags.EXECUTION_PLAN_VALIDATION_ENABLED:
                from omlx.planner.planner import ExecutionPlanner
                from omlx.planner.compatibility import ExecutionProfileAdapter
                from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily

                # Mock capability resolution for now if actual resolver isn't integrated yet
                # In full implementation, we'd use CapabilityResolver.resolve() here
                # but we'll use a placeholder for equivalence testing based on the context

                planner = ExecutionPlanner()

                # Create a capability descriptor based on actual_caps to pass to planner
                # This simulates CapabilityResolver output
                family = ExecutionFamily.AUTOREGRESSIVE
                if actual_caps.supports_diffusion:
                    family = ExecutionFamily.DIFFUSION
                elif getattr(model_caps, "model_type", "") == "embedding":
                    family = ExecutionFamily.EMBEDDING

                descriptor = CapabilityDescriptor(
                    execution_family=family,
                    supports_streaming=True, # default
                    supports_speculative=getattr(actual_caps, "supports_linear_spec", False)
                )

                plan = planner.plan(descriptor)

                # Compatibility layer
                if flags.EXECUTION_PROFILE_COMPATIBILITY_ENABLED or flags.EXECUTION_PLAN_RUNTIME_ENABLED:
                    plan_profile = ExecutionProfileAdapter.adapt(plan)

                    if flags.EXECUTION_PLAN_VALIDATION_ENABLED:
                        # Log any differences
                        differences = []
                        if profile.backend_name != plan_profile.backend_name and not (profile.backend_name == 'experimental_nemotron' and plan_profile.backend_name == 'diffusion'):
                             differences.append(f"backend: {profile.backend_name} != {plan_profile.backend_name}")
                        if differences:
                             logger.warning(f"Planning equivalence verification failed: {', '.join(differences)}")
                        else:
                             logger.debug("Planning equivalence verification passed")

                    if flags.EXECUTION_PLAN_RUNTIME_ENABLED:
                        # Use the plan-derived profile!
                        profile = plan_profile

                        # Note: we still need to get the factory. In the long term, we remove this too.
                        # For now, look it up in the registry based on backend_name
                        factory = profile_registry._factories.get(profile.backend_name)
                        if factory is None and profile.backend_name == "diffusion":
                             # fallback mapping for testing
                             factory = profile_registry._factories.get("experimental_nemotron")
                        if factory is None:
                             # fallback
                             factory = profile_registry._factories.get("autoregressive")

                        backend_factory = factory"""

content = content.replace(old_block, new_block)

with open("omlx/engine_core.py", "w") as f:
    f.write(content)
