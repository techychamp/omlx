# SPDX-License-Identifier: Apache-2.0
"""
Tests for TransformerExecutionEngine.
"""

from unittest.mock import MagicMock
import pytest

from omlx.request import SamplingParams
from omlx.inference.execution_engine import TransformerExecutionEngine


def test_transformer_execution_engine_initial_state():
    engine = TransformerExecutionEngine(batch_generator=None)
    assert not engine.has_generator()
    assert engine.forward() == []
    assert engine.eval_cache() == 0
    assert engine.extract_cache(42) is None


def test_transformer_execution_engine_delegation():
    mock_bg = MagicMock()
    mock_bg.insert.return_value = [42]
    mock_bg.extract_cache.return_value = {42: ([], [1, 2])}
    
    engine = TransformerExecutionEngine(batch_generator=mock_bg)
    assert engine.has_generator()
    
    # Test insert delegation
    uids = engine.insert(tokens=[1])
    mock_bg.insert.assert_called_once_with(tokens=[1])
    assert uids == [42]
    
    # Test remove delegation
    engine.remove([42])
    mock_bg.remove.assert_called_once_with([42])
    
    # Test extract_cache delegation
    res = engine.extract_cache([42])
    mock_bg.extract_cache.assert_called_once_with([42])
    assert res == {42: ([], [1, 2])}
    
    # Test forward delegation
    mock_bg.next_generated.return_value = iter([1, 2])
    res_f = list(engine.forward())
    mock_bg.next_generated.assert_called_once()
    assert res_f == [1, 2]


def test_transformer_execution_engine_ensure_generator(monkeypatch):
    engine = TransformerExecutionEngine(batch_generator=None)
    
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_tokens=100,
        stop_token_ids={3},
    )
    
    mock_bg_class = MagicMock()
    monkeypatch.setattr("omlx.inference.execution_engine.BatchGenerator", mock_bg_class)
    
    scheduler = MagicMock()
    scheduler.model = MagicMock()
    scheduler.config = MagicMock()
    scheduler.config.completion_batch_size = 4
    scheduler.config.prefill_step_size = 32
    scheduler._stream = MagicMock()
    scheduler._get_stop_tokens.return_value = {2}
    scheduler._xtc_special_tokens = []
    scheduler._model_suppress_tokens = set()
    scheduler._output_parser_factory = None
    
    engine.ensure_generator(scheduler, sampling_params)
    
    assert mock_bg_class.called
    assert engine.batch_generator is not None
