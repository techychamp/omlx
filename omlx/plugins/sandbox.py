from enum import Enum
from dataclasses import dataclass, field

class SandboxIsolationLevel(Enum):
    SHARED = "shared"
    ISOLATED_STATE = "isolated_state"
    READ_ONLY = "read_only"
    PROCESS_ISOLATION = "process_isolation"
    WASM_EXECUTION = "wasm_execution"
    CONTAINER_EXECUTION = "container_execution"

@dataclass(frozen=True)
class PluginSandboxPolicy:
    isolation_level: SandboxIsolationLevel = SandboxIsolationLevel.SHARED
    thread_safe: bool = True
