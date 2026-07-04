# SPDX-License-Identifier: Apache-2.0
"""
Execution constraints for backend intelligence framework.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionConstraints:
    max_graph_size: int = -1
    max_sequence_length: int = -1
    preferred_batch_size: int = 1
    preferred_concurrency: int = 1
    preferred_execution_family: str = ""
    preferred_scheduling_mode: str = ""
    memory_limit_bytes: int = -1
    cache_limit_bytes: int = -1
    streaming_limit_bytes: int = -1
    verification_limit: int = -1
    expert_limit: int = -1
