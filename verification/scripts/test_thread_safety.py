# SPDX-License-Identifier: Apache-2.0
"""Test Thread Safety across verification frameworks."""

import pytest
import concurrent.futures
from types import MappingProxyType
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily, CacheLayoutType, AttentionType
from verification.scripts.utils import GoldenComparator

def test_thread_safety_golden_comparator():
    """Verify that GoldenComparator operates safely under concurrent load."""

    dict_a = {"a": 1, "b": {"c": [1, 2, 3]}, "d": "string"}
    dict_b = {"a": 1, "b": {"c": [1, 2, 3]}, "d": "string"}
    dict_c = {"a": 2, "b": {"c": [1, 2]}, "e": "new"}

    def run_compare(mode):
        if mode == "equal":
            diff = GoldenComparator.compare(dict_a, dict_b)
            assert not diff.has_differences()
        else:
            diff = GoldenComparator.compare(dict_a, dict_c)
            assert diff.has_differences()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(50):
            mode = "equal" if i % 2 == 0 else "diff"
            futures.append(executor.submit(run_compare, mode))

        for future in concurrent.futures.as_completed(futures):
            future.result() # Will raise assertion error if any failed

def test_thread_safety_execution_planner():
    """Verify that the immutable ExecutionPlanner logic can be executed concurrently."""

    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supports_speculative=False,
        supports_streaming=True,
        supports_verification=False,
        cache_layout=CacheLayoutType.PAGED,
        attention_types=(AttentionType.CAUSAL,),
        hardware_requirements=tuple(),
        execution_hints=MappingProxyType({})
    )

    planner = ExecutionPlanner()

    def run_plan():
        plan = planner.plan(descriptor)
        assert plan.execution_backend == "autoregressive"
        assert plan.execution_mode == "streaming"

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_plan) for _ in range(50)]
        for future in concurrent.futures.as_completed(futures):
            future.result()
