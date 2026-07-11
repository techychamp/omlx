# SPDX-License-Identifier: Apache-2.0
"""
Tests for ExecutionBackend and AutoregressiveBackend.
"""

from unittest.mock import MagicMock
import pytest

from omlx.inference.backends.autoregressive_backend import AutoregressiveBackend
from omlx.inference.execution_engine import TransformerExecutionEngine
from omlx.inference.execution_backend import PipelineState


def test_autoregressive_backend_initialization():
    engine = TransformerExecutionEngine(batch_generator=MagicMock())
    backend = AutoregressiveBackend(engine)
    
    assert backend.runtime.engine == engine
    assert backend.pipeline is not None
    assert backend.validate().is_valid
    
    plan = backend.plan()
    assert len(plan.steps) > 0
    assert "ForwardStage" in plan.steps


def test_autoregressive_backend_execute_cycle():
    mock_bg = MagicMock()
    mock_bg.next_generated.return_value = iter([MagicMock(uid=1, token=100)])
    
    engine = TransformerExecutionEngine(batch_generator=mock_bg)
    backend = AutoregressiveBackend(engine)
    
    res = list(backend.execute_cycle(inputs=None))
    assert res is not None
    assert len(res) > 0
    assert res[0].token == 100
