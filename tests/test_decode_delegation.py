# SPDX-License-Identifier: Apache-2.0
"""
Tests for decode delegation from Scheduler to GenerationStrategy.
"""

from unittest.mock import MagicMock, patch
import pytest
import gc

from omlx.request import Request, RequestOutput, SamplingParams
from omlx.scheduler import Scheduler, SchedulerConfig
from omlx.inference.strategies.autoregressive import AutoregressiveStrategy


def _make_scheduler() -> Scheduler:
    model = MagicMock()
    model.layers = []
    
    tokenizer = MagicMock()
    tokenizer.eos_token_id = 2
    
    config = SchedulerConfig(
        max_num_seqs=8,
        prefill_step_size=4,
        chunked_prefill=False,
        paged_cache_block_size=0,
    )
    
    scheduler = Scheduler(model=model, tokenizer=tokenizer, config=config)
    return scheduler


class MockResponse:
    def __init__(self, uid: int, token: int, finish_reason: str | None = None):
        self.uid = uid
        self.token = token
        self.finish_reason = finish_reason


def test_scheduler_delegates_decode_when_strategy_bound():
    scheduler = _make_scheduler()
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
    scheduler.set_strategy(strategy)
    
    # Setup mock batch generator
    mock_bg = MagicMock()
    mock_bg.next_generated.return_value = iter([MockResponse(uid=42, token=100)])
    scheduler.batch_generator = mock_bg
    
    # Configure scheduler running/waiting state
    req = Request(
        request_id="req-1",
        prompt=[1, 2, 3],
        sampling_params=SamplingParams(max_tokens=32),
    )
    scheduler.running = {"req-1": req}
    scheduler.uid_to_request_id = {42: "req-1"}
    scheduler.request_id_to_uid = {"req-1": 42}
    
    # Spy/mock the strategy forward
    strategy.forward = MagicMock(side_effect=strategy.forward)
    
    scheduler.step()
    
    # Verify strategy.forward was called exactly once
    assert strategy.forward.call_count == 1
    # Verify next_generated was called exactly once through strategy
    assert mock_bg.next_generated.call_count == 1


def test_scheduler_falls_back_when_no_strategy_bound():
    scheduler = _make_scheduler()
    
    # Setup mock batch generator
    mock_bg = MagicMock()
    mock_bg.next_generated.return_value = iter([MockResponse(uid=42, token=100)])
    scheduler.batch_generator = mock_bg
    
    # Configure scheduler running state
    req = Request(
        request_id="req-1",
        prompt=[1, 2, 3],
        sampling_params=SamplingParams(max_tokens=32),
    )
    scheduler.running = {"req-1": req}
    scheduler.uid_to_request_id = {42: "req-1"}
    
    scheduler.step()
    
    # Verify next_generated was called directly on batch generator
    assert mock_bg.next_generated.call_count == 1


def test_equivalence_delegated_vs_fallback():
    # Helper to run a step and extract outputs/state
    def run_scheduler_test(use_strategy: bool):
        scheduler = _make_scheduler()
        if use_strategy:
            strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
            scheduler.set_strategy(strategy)
            
        mock_bg = MagicMock()
        mock_bg.next_generated.return_value = iter([MockResponse(uid=42, token=100, finish_reason="stop")])
        scheduler.batch_generator = mock_bg
        
        req = Request(
            request_id="req-1",
            prompt=[1, 2, 3],
            sampling_params=SamplingParams(max_tokens=32),
        )
        scheduler.running = {"req-1": req}
        scheduler.uid_to_request_id = {42: "req-1"}
        scheduler.request_id_to_uid = {"req-1": 42}
        
        output = scheduler.step()
        return output, scheduler.running, scheduler.waiting
        
    output_strat, running_strat, waiting_strat = run_scheduler_test(use_strategy=True)
    output_fall, running_fall, waiting_fall = run_scheduler_test(use_strategy=False)
    
    # Verify token equivalence
    assert len(output_strat.outputs) == len(output_fall.outputs)
    assert output_strat.outputs[0].request_id == output_fall.outputs[0].request_id
    assert output_strat.outputs[0].new_token_ids == output_fall.outputs[0].new_token_ids
    assert output_strat.outputs[0].finish_reason == output_fall.outputs[0].finish_reason
    
    # Verify scheduler invariants (queues/states match)
    assert list(running_strat.keys()) == list(running_fall.keys())
    assert list(waiting_strat) == list(waiting_fall)
    assert output_strat.finished_request_ids == output_fall.finished_request_ids


def test_memory_stability_and_leaks():
    scheduler = _make_scheduler()
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
    scheduler.set_strategy(strategy)
    
    mock_bg = MagicMock()
    # Return a generator that yields a token
    def gen_func():
        yield MockResponse(uid=42, token=100)
    mock_bg.next_generated.side_effect = gen_func
    scheduler.batch_generator = mock_bg
    
    req = Request(
        request_id="req-1",
        prompt=[1, 2, 3],
        sampling_params=SamplingParams(max_tokens=1000),
    )
    scheduler.running = {"req-1": req}
    scheduler.uid_to_request_id = {42: "req-1"}
    scheduler.request_id_to_uid = {"req-1": 42}
    
    # Run repeated decode steps to trace memory stability/leaks
    gc.collect()
    
    def count_instances(cls):
        count = 0
        for obj in gc.get_objects():
            try:
                if type(obj) is cls:
                    count += 1
            except Exception:
                pass
        return count

    initial_requests = count_instances(Request)
    initial_responses = count_instances(MockResponse)
    
    for _ in range(50):
        # Reset side effect generator so it doesn't run out
        mock_bg.next_generated.side_effect = gen_func
        scheduler.step()
        
    gc.collect()
    final_requests = count_instances(Request)
    final_responses = count_instances(MockResponse)
    
    # Verify no progressive leaks of core objects
    assert final_requests == initial_requests
    assert final_responses - initial_responses <= 1


def test_long_running_stability():
    scheduler = _make_scheduler()
    strategy = AutoregressiveStrategy(scheduler=scheduler, backend=None)
    scheduler.set_strategy(strategy)
    
    mock_bg = MagicMock()
    
    # Setup state for a long running decode of 500 iterations
    req = Request(
        request_id="req-1",
        prompt=[1, 2, 3],
        sampling_params=SamplingParams(max_tokens=1000),
    )
    scheduler.running = {"req-1": req}
    scheduler.uid_to_request_id = {42: "req-1"}
    scheduler.request_id_to_uid = {"req-1": 42}
    
    for i in range(500):
        # Yield one token at each iteration
        mock_bg.next_generated.return_value = iter([MockResponse(uid=42, token=i)])
        scheduler.batch_generator = mock_bg
        
        output = scheduler.step()
        
        # Verify queue sizes remain stable
        assert len(scheduler.running) == 1
        assert len(scheduler.waiting) == 0
        assert len(output.outputs) == 1
        assert output.outputs[0].new_token_ids == [i]
