# SPDX-License-Identifier: Apache-2.0
"""
Tests for MLXAdapter execution of backend operations.
"""

from unittest.mock import MagicMock
import pytest

from omlx.planner.compiler.backend.adapter import MLXAdapter
from omlx.planner.compiler.backend.operations import (
    MLXForwardOperation,
    MLXSynchronizationOperation,
    MLXCacheLookupOperation,
    MLXCacheUpdateOperation,
    MLXSamplingOperation,
    MLXNoOpOperation,
)
from omlx.runtime.execution.context import ExecutionContext

class MockRequestContext:
    def __init__(self):
        self.input_ids = [10, 20, 30]

class MockModel:
    def __call__(self, input_ids):
        class MockLogits:
            shape = (1, len(input_ids), 32000)
        return MockLogits()

def test_mlx_adapter_forward_no_model():
    adapter = MLXAdapter()
    op = MLXForwardOperation("test_fwd")
    context = ExecutionContext()

    result = adapter.execute(op, context)
    assert result["status"] == "executed"
    assert "simulated_logits" in result["result"]["logits"]
    assert any("No model in ExecutionContext" in d for d in result["diagnostics"])

def test_mlx_adapter_forward_with_model():
    adapter = MLXAdapter()
    op = MLXForwardOperation("test_fwd")
    context = ExecutionContext(model=MockModel(), request_context=MockRequestContext())

    result = adapter.execute(op, context)
    assert result["status"] == "executed"
    assert "logits_shape" in result["result"]

def test_mlx_adapter_synchronization():
    adapter = MLXAdapter()
    op = MLXSynchronizationOperation("test_sync")
    context = ExecutionContext()

    result = adapter.execute(op, context)
    assert result["status"] == "executed"

def test_mlx_adapter_cache_operations():
    adapter = MLXAdapter()
    context = ExecutionContext()

    op_lookup = MLXCacheLookupOperation("test_lookup")
    result1 = adapter.execute(op_lookup, context)
    assert result1["status"] == "executed"

    op_update = MLXCacheUpdateOperation("test_update")
    result2 = adapter.execute(op_update, context)
    assert result2["status"] == "executed"

def test_mlx_adapter_sampling_operation():
    adapter = MLXAdapter()
    op = MLXSamplingOperation("test_sample")
    context = ExecutionContext()

    result = adapter.execute(op, context)
    assert result["status"] == "unsupported"
    assert any("not a backend responsibility" in d for d in result["diagnostics"])

def test_mlx_adapter_noop_operation():
    adapter = MLXAdapter()
    op = MLXNoOpOperation("test_noop")
    context = ExecutionContext()

    result = adapter.execute(op, context)
    assert result["status"] == "executed"
