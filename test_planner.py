from omlx.planner.cache_planner import CachePlanner
from omlx.runtime.feature_flags import FeatureFlags
from omlx.framework.cache.descriptor import CacheDescriptor

flags = FeatureFlags()
flags.CACHE_PLANNING_ENABLED = True
planner = CachePlanner(flags)

desc = CacheDescriptor(cache_type="paged", capacity=1024, element_size=8)
plan = planner.plan(desc)

print(f"Plan ID: {plan.plan_id}")
print(f"Allocation Strategy: {plan.allocation_strategy}")
