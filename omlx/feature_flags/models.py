from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any, Callable

class FlagLifecycle(str, Enum):
    SHADOW = "shadow"
    EXPERIMENTAL = "experimental"
    DUAL_RUN = "dual_run"
    VALIDATION = "validation"
    PRIMARY = "primary"
    DEPRECATED = "deprecated"
    REMOVED = "removed"

class FlagCategory(str, Enum):
    RUNTIME = "runtime"
    EXECUTION = "execution"
    PLANNER = "planner"
    ADAPTER = "adapter"
    PLUGIN = "plugin"
    VERIFICATION = "verification"
    DEVELOPER = "developer"
    EXPERIMENTAL = "experimental"
    INTERNAL = "internal"

class FlagType(str, Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"

class FeatureFlag(BaseModel):
    name: str
    description: str
    category: FlagCategory
    lifecycle: FlagLifecycle
    flag_type: FlagType = FlagType.BOOLEAN
    default_value: Any
    owner: str
    creation_checkpoint: str
    removal_checkpoint: Optional[str] = None
    env_var_name: Optional[str] = None
