# SPDX-License-Identifier: Apache-2.0
"""
Tests for prefill delegation from Scheduler to GenerationStrategy.
"""

from unittest.mock import MagicMock, patch
import pytest
import mlx.core as mx

from omlx.request import Request, SamplingParams
from omlx.scheduler import Scheduler, SchedulerConfig
from omlx.inference.strategies.autoregressive import AutoregressiveStrategy
from omlx.inference.strategies.diffusion import DiffusionStrategy


def _make_scheduler(chunked_prefill: bool = False, step_size: int = 4) -> Scheduler:
    model = MagicMock()
    model.layers = []
    
    tokenizer = MagicMock()
    tokenizer.eos_token_id = 2
    
    config = SchedulerConfig(
        max_num_seqs=8,
        prefill_step_size=step_size,
        chunked_prefill=chunked_prefill,
        paged_cache_block_size=0,
    )
    
    scheduler = Scheduler(model=model, tokenizer=tokenizer, config=config)
    
    # Mock BatchGenerator setup to avoid real insertion logic complexity
    mock_bg = MagicMock()
    mock_bg.insert.return_value = [42]
    mock_bg.next_generated.return_value = iter([])
    scheduler.batch_generator = mock_bg
    scheduler._current_sampler_params = ()
    
    return scheduler


def _make_request(request_id: str = "req-1", n_tokens: int = 10) -> Request:
    req = Request(
        request_id=request_id,
        prompt=list(range(n_tokens)),
        sampling_params=SamplingParams(max_tokens=32),
    )
    req.prompt_token_ids = list(range(n_tokens))
    req.num_prompt_tokens = n_tokens
    req.remaining_tokens = list(range(n_tokens))
    return req


def test_autoregressive_strategy_inherits_prefill():
    # Verify that AutoregressiveStrategy has a callable prefill method (inherited)
    strategy = AutoregressiveStrategy(scheduler=None, backend=None)
    assert hasattr(strategy, "prefill")
    assert callable(strategy.prefill)


def test_diffusion_strategy_raises_not_implemented():
    strategy = DiffusionStrategy(scheduler=None, backend=None)
    with pytest.raises(NotImplementedError, match="Diffusion strategy does not support standard AR-style prefill"):
        strategy.prefill(model=MagicMock(), inputs=MagicMock(), cache=MagicMock())


def test_scheduler_delegates_prefill_normal():
    scheduler = _make_scheduler(chunked_prefill=False)
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
    scheduler.set_strategy(strategy)
    
    # Spy/mock the prefill method
    original_prefill = strategy.prefill
    strategy.prefill = MagicMock(side_effect=original_prefill)
    
    req = _make_request(n_tokens=5)
    scheduler.requests[req.request_id] = req
    scheduler.waiting.append(req)
    
    # Mock make_prompt_cache
    mock_cache = [MagicMock()]
    mock_cache[0].state = mx.array([1, 2, 3])
    
    with patch("omlx.scheduler.make_prompt_cache", return_value=mock_cache) as mock_make_cache:
        scheduler.step()
        
        # Verify that strategy.prefill was called exactly once
        assert strategy.prefill.call_count == 1
        
        # Verify call arguments
        call_args = strategy.prefill.call_args[0]
        call_kwargs = strategy.prefill.call_args[1]
        # (model, inputs)
        assert call_args[0] == scheduler.model
        # inputs: mx.array shape (1, N-1) where prompt size is 5, so n-1 = 4 tokens prefilled
        assert call_args[1].tolist() == [[0, 1, 2, 3]]
        assert call_kwargs["cache"] == mock_cache
        
        # Verify that scheduler's model was called (delegated through strategy.prefill)
        assert scheduler.model.call_count == 1


def test_scheduler_delegates_prefill_chunked():
    scheduler = _make_scheduler(chunked_prefill=True, step_size=2)
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
    scheduler.set_strategy(strategy)
    
    strategy.prefill = MagicMock(side_effect=strategy.prefill)
    
    req = _make_request(n_tokens=5)
    scheduler.requests[req.request_id] = req
    scheduler.waiting.append(req)
    
    mock_cache = [MagicMock()]
    mock_cache[0].state = mx.array([1, 2, 3])
    
    with patch("omlx.scheduler.make_prompt_cache", return_value=mock_cache):
        # Step 1: Begins prefill, processes first chunk (2 tokens: 0, 1)
        scheduler.step()
        assert strategy.prefill.call_count == 1
        assert strategy.prefill.call_args[0][1].tolist() == [[0, 1]]
        
        # Step 2: Processes second chunk (2 tokens: 2, 3)
        scheduler.step()
        assert strategy.prefill.call_count == 2
        assert strategy.prefill.call_args[0][1].tolist() == [[2, 3]]
        
        # Verify scheduler queues: the request is now in running
        assert req.request_id in scheduler.running


def test_cache_equivalence():
    # Setup two schedulers: one with strategy, one without (fallback)
    sched_strat = _make_scheduler(chunked_prefill=False)
    strategy = AutoregressiveStrategy(scheduler=sched_strat, backend=None)
    sched_strat.set_strategy(strategy)
    
    sched_fallback = _make_scheduler(chunked_prefill=False)
    # No strategy set
    
    req_strat = _make_request(request_id="req-strat", n_tokens=5)
    sched_strat.requests[req_strat.request_id] = req_strat
    sched_strat.waiting.append(req_strat)
    
    req_fallback = _make_request(request_id="req-fallback", n_tokens=5)
    sched_fallback.requests[req_fallback.request_id] = req_fallback
    sched_fallback.waiting.append(req_fallback)
    
    # Capture model calls to track cache mutation
    cache_strat = [MagicMock()]
    cache_strat[0].state = mx.array([1.0, 2.0])
    
    cache_fallback = [MagicMock()]
    cache_fallback[0].state = mx.array([1.0, 2.0])
    
    def mock_model_call(inputs, cache=None, **kwargs):
        # Mutate state in mock model call
        cache[0].state = cache[0].state + 1.0
    
    sched_strat.model.side_effect = mock_model_call
    sched_fallback.model.side_effect = mock_model_call
    
    with patch("omlx.scheduler.make_prompt_cache") as mock_make_cache:
        mock_make_cache.side_effect = [cache_strat, cache_fallback]
        
        sched_strat.step()
        sched_fallback.step()
        
        # Verify that both mutated cache states are identical
        assert mx.allclose(cache_strat[0].state, cache_fallback[0].state)
        assert cache_strat[0].state.tolist() == [2.0, 3.0]
        assert cache_fallback[0].state.tolist() == [2.0, 3.0]


def test_scheduler_state_invariants():
    # Verify that scheduler queues and stats are unaffected by strategy binding
    scheduler = _make_scheduler(chunked_prefill=True, step_size=2)
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
    scheduler.set_strategy(strategy)
    
    req = _make_request(n_tokens=5)
    scheduler.requests[req.request_id] = req
    scheduler.waiting.append(req)
    
    mock_cache = [MagicMock()]
    mock_cache[0].state = mx.array([1, 2, 3])
    
    with patch("omlx.scheduler.make_prompt_cache", return_value=mock_cache):
        scheduler.step()
        # Request should now be in the self.prefilling queue
        assert len(scheduler.prefilling) == 1
        assert scheduler.prefilling[0] == req
        assert len(scheduler.running) == 0
        
        scheduler.step()
        # Now it is fully processed and inserted into running
        assert len(scheduler.prefilling) == 0
        assert len(scheduler.running) == 1
        assert scheduler.running[req.request_id] == req
