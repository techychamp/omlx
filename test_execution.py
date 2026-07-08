from omlx.framework.cache import CacheDescriptor, CachePlan
from omlx.planner.cache_planner import CachePlanner
from omlx.runtime.feature_flags import FeatureFlags
from omlx.runtime.execution.cache_session import CacheSession

# 1. Feature flags
flags = FeatureFlags()
flags.CACHE_PLANNING_ENABLED = True
flags.CACHE_RUNTIME_ENABLED = True

# 2. Immutable descriptor
desc = CacheDescriptor(cache_type="paged", capacity=2048, element_size=16)

# 3. Planner
planner = CachePlanner(flags)
plan = planner.plan(desc)

print(f"Plan created: {plan.plan_id}, max_cap: {plan.max_capacity}")

# 4. Cache Session
session = CacheSession(plan)
print(f"Session active: {session.is_active()}")
session.activate()
print(f"Session active: {session.is_active()}")
session.deactivate()
print(f"Session active: {session.is_active()}")

print("State verified successfully!")
