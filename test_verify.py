from omlx.runtime.feature_flags import FeatureFlags
from omlx.planner.cache_planner import CachePlanner
from omlx.runtime.execution.cache_session import CacheSession
from omlx.runtime.execution.engine import ExecutionEngine
from omlx.runtime.compiler_service import CompilerSession
from omlx.runtime.generation.standard import StandardGenerationStrategy
from omlx.runtime.generation.speculative import SpeculativeGenerationStrategy
from omlx.framework.cache.descriptor import CacheDescriptor

flags = FeatureFlags()
assert hasattr(flags, 'CACHE_PLANNING_ENABLED')

planner = CachePlanner(flags)
desc = CacheDescriptor(cache_type='paged', capacity=1024, element_size=8)
plan = planner.plan(desc)

if flags.CACHE_PLANNING_ENABLED:
    assert plan is not None

session = CacheSession(plan)
assert not session.is_active()

engine = ExecutionEngine()
assert engine is not None

std = StandardGenerationStrategy()
assert std.get_cache_policy()['policy'] == 'standard'

spec = SpeculativeGenerationStrategy()
assert spec.get_cache_policy()['policy'] == 'speculative'

print("All components verified successfully without pytest.")
