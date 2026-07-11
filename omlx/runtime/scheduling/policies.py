# SPDX-License-Identifier: Apache-2.0
"""
Scheduling Policies for OMLX runtime.
"""

import enum

class SchedulingPolicy(enum.Enum):
    SEQUENTIAL = "sequential"
    DEPENDENCY_DRIVEN = "dependency_driven"
    LATENCY_OPTIMIZED = "latency_optimized"
    MEMORY_OPTIMIZED = "memory_optimized"
    THROUGHPUT_OPTIMIZED = "throughput_optimized"
    DEBUG = "debug"
