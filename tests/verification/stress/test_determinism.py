# SPDX-License-Identifier: Apache-2.0
"""
Determinism verification testing.
Verifies that multiple compilations of the same graph/inputs yield bit-for-bit identical schedules/artifacts.
"""

import pytest
from unittest.mock import MagicMock
from collections import namedtuple

from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.policies import SchedulingPolicy

MockGraph = namedtuple("MockGraph", ["operations"])
MockOp = namedtuple("MockOp", ["dependencies"])

def test_end_to_end_compiler_determinism():
    """Verify that multiple consecutive scheduling builds for the same graph result in identical output."""
    scheduler = GraphScheduler(policy=SchedulingPolicy.DEPENDENCY_DRIVEN)

    # A slightly complex graph to test stable topological sorting and queue extraction
    graph = MockGraph(operations={
        "NodeD": MockOp(dependencies=["NodeA", "NodeB"]),
        "NodeC": MockOp(dependencies=["NodeA"]),
        "NodeB": MockOp(dependencies=["NodeA"]),
        "NodeA": MockOp(dependencies=[])
    })

    schedules = []

    # Run scheduling 10 times
    for _ in range(10):
        schedules.append(scheduler.build_schedule(graph))

    first_schedule = schedules[0]

    for i in range(1, 10):
        # Ordered operations must be exactly identical
        assert schedules[i].ordered_operations == first_schedule.ordered_operations

        # Dependency levels must be identical
        assert schedules[i].dependency_levels == first_schedule.dependency_levels

        # Critical paths must match
        assert schedules[i].critical_path == first_schedule.critical_path

        # Queues must match
        assert schedules[i].ready_queues == first_schedule.ready_queues

        # Metadata check
        assert schedules[i].metadata["policy"] == first_schedule.metadata["policy"]
