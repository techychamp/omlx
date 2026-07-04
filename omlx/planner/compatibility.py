from typing import Dict, Any
from omlx.planner.plan import ExecutionPlan
from omlx.inference.execution_profile import ExecutionProfile
from omlx.capabilities.descriptor import CacheLayoutType

class ExecutionProfileAdapter:
    """Translates an ExecutionPlan into a legacy ExecutionProfile.

    This adapter contains zero planning logic and relies entirely on
    static mapping tables and direct field forwarding. All default values
    must originate from the ExecutionPlan or ExecutionProfile definitions.
    """

    # Static mapping tables for enumerations that differ between layers
    CACHE_MODE_MAP: Dict[CacheLayoutType, str] = {
        CacheLayoutType.PAGED: "standard",
        CacheLayoutType.CONTINUOUS: "standard",
        CacheLayoutType.RADIX_TREE: "standard",
        CacheLayoutType.NONE: "standard",
    }

    @classmethod
    def adapt(cls, plan: ExecutionPlan) -> ExecutionProfile:
        kwargs: Dict[str, Any] = {}

        # Field 1: backend_name (canonical mapped field)
        kwargs["backend_name"] = plan.execution_backend

        # Field 2: cache_mode (mapped via static table)
        if plan.cache_strategy in cls.CACHE_MODE_MAP:
             kwargs["cache_mode"] = cls.CACHE_MODE_MAP[plan.cache_strategy]

        # Field 3: streaming_mode (mapped from execution_mode)
        # In legacy, 'streaming_mode' is effectively the execution mode
        kwargs["streaming_mode"] = plan.execution_mode

        # Field 4-7: Direct forwarding from hints if they exist
        for hint_key in ["attention_mode", "sampler_mode", "position_encoding", "version"]:
             if hint_key in plan.execution_hints:
                  kwargs[hint_key] = plan.execution_hints[hint_key]

        return ExecutionProfile(**kwargs)
