# SPDX-License-Identifier: Apache-2.0
"""
Integration tests for Backend, Pipeline, and Engine.
"""

from unittest.mock import MagicMock
import pytest

from omlx.inference.strategies.autoregressive import AutoregressiveStrategy
from omlx.inference.backends.autoregressive_backend import AutoregressiveBackend
from omlx.inference.execution_engine import TransformerExecutionEngine
from omlx.request import Request, SamplingParams
from omlx.scheduler import Scheduler, SchedulerConfig


class MockResponse:
    def __init__(self, uid: int, token: int):
        self.uid = uid
        self.token = token
        self.finish_reason = None


def test_strategy_backend_engine_integration():
    # Setup mocks
    model = MagicMock()
    tokenizer = MagicMock()
    tokenizer.eos_token_id = 2
    config = SchedulerConfig(
        max_num_seqs=8,
        prefill_step_size=4,
        chunked_prefill=False,
        paged_cache_block_size=0,
    )
    
    scheduler = Scheduler(model=model, tokenizer=tokenizer, config=config)
    
    # Instantiate engine, backend, and strategy
    mock_bg = MagicMock()
    mock_bg.insert.return_value = [42]
    mock_bg.next_generated.return_value = iter([MockResponse(uid=42, token=100)])
    
    engine = TransformerExecutionEngine(batch_generator=mock_bg)
    backend = AutoregressiveBackend(engine)
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=backend)
    scheduler.set_strategy(strategy)
    
    # Test ensure_generator
    sampling_params = SamplingParams(max_tokens=10)
    strategy.ensure_generator(sampling_params)
    
    # Test insert
    uids = strategy.insert(
        [[1, 2]],
        max_tokens=[10],
        caches=None,
        all_tokens=[[1, 2]],
        samplers=[MagicMock()],
        logits_processors=[[]],
        state_machines=[MagicMock()]
    )
    assert uids == [42]
    mock_bg.insert.assert_called_once()
    
    # Configure scheduler running state
    req = Request(
        request_id="req-1",
        prompt=[1, 2, 3],
        sampling_params=sampling_params,
    )
    scheduler.running = {"req-1": req}
    scheduler.uid_to_request_id = {42: "req-1"}
    scheduler.request_id_to_uid = {"req-1": 42}
    
    # Run step and verify execution flow
    output = scheduler.step()
    assert len(output.outputs) == 1
    assert output.outputs[0].new_token_ids == [100]
    
    # Test remove
    strategy.remove([42])
    mock_bg.remove.assert_called_once_with([42])
