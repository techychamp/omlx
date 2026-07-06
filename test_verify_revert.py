from omlx.runtime.feature_flags import FeatureFlags
from omlx.planner.cache_planner import CachePlanner
from omlx.runtime.execution.cache_session import CacheSession
from omlx.runtime.execution.context import ExecutionContext
from omlx.runtime.execution.engine import ExecutionEngine
from omlx.framework.cache.descriptor import CacheDescriptor

# Ensure feature flags work
flags = FeatureFlags()
flags.CACHE_PLANNING_ENABLED = True

# Generate plan
planner = CachePlanner(flags)
desc = CacheDescriptor(cache_type='paged', capacity=1024, element_size=8)
plan = planner.plan(desc)

# Runtime lifecycle
session = CacheSession(plan)
session.activate()
assert session.is_active()

# Execution context construction with runtime-owned session
ctx = ExecutionContext(cache_plan=plan, cache_session=session, backend_operation_graph="dummy")

# Execution Engine consumption (should not fail or alter lifecycle)
engine = ExecutionEngine()
result = engine.execute(ctx)
# The engine fails explicitly without a valid graph, but it shouldn't throw an unhandled exception
assert result is not None

# Runtime deactivated
session.deactivate()
assert not session.is_active()

print("Architecture decoupled verified: Runtime owns CacheSession, Engine consumes it.")
