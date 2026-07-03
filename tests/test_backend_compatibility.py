import unittest
from typing import Any
import mlx.core as mx

from omlx.scheduler import Scheduler
from omlx.request import Request, SamplingParams
from omlx.inference.execution_backend import (
    ExecutionBackend, ExecutionPipeline, ExecutionEngine,
    ExecutionRuntime, ExecutionContract, BackendStatus, ExecutionPlan, PipelineState,
    ExecuteCycleCommand
)
from omlx.inference.modes import GenerationMode

class FakeEngine(ExecutionEngine):
    pass

class FakeRuntime(ExecutionRuntime):
    def __init__(self):
        self._engine = FakeEngine()
    @property
    def engine(self): return self._engine

class FakePipeline(ExecutionPipeline):
    def __init__(self):
        super().__init__(stages=[])
        self.executed = False
    
    def describe(self) -> str: return "FakePipeline"
    def execute(self, inputs: Any, runtime: ExecutionRuntime) -> Any:
        self.executed = True
        return inputs

class FakeBackend(ExecutionBackend):
    def __init__(self):
        self._runtime = FakeRuntime()
        self._pipeline = FakePipeline()
        self.prepared = False
    
    @property
    def runtime(self): return self._runtime
    @property
    def pipeline(self): return self._pipeline
    @property
    def contract(self):
        return ExecutionContract(
            supported_commands={ExecuteCycleCommand},
            supported_events=set(),
            supported_states={PipelineState.INITIALIZED},
            supported_pipeline=self._pipeline.metadata,
            required_capabilities=set(),
            runtime_requirements={}
        )
    
    def validate(self): return BackendStatus(is_valid=True)
    def plan(self): return ExecutionPlan(steps=["fake"], estimated_memory_bytes=0)
    def prepare(self, *args, **kwargs): self.prepared = True
    def execute(self, inputs): return self.pipeline.execute(inputs, self.runtime)
    def synchronize(self): pass
    def finalize(self, *args, **kwargs): pass
    def cleanup(self): pass

class TestBackendCompatibility(unittest.TestCase):
    def test_fake_backend_integration(self):
        # Create a scheduler without starting background threads
        # We will mock the config
        from unittest.mock import MagicMock, patch
        config = MagicMock()
        config.model_name = "test_model"
        config.completion_batch_size = 1
        config.cache_size_mb = 128
        config.kv_cache_type = "paged"
        config.max_kv_cache_size = 1000
        config.enable_paged_cache = False
        config.block_size = 16
        
        # Instantiate scheduler
        # We need to mock tokenizer and model
        with patch("omlx.scheduler.PagedCacheManager"):
            scheduler = Scheduler(model=MagicMock(), tokenizer=MagicMock(), config=config)
        
        # Replace AR strategy backend with FakeBackend
        from omlx.inference.strategies.autoregressive import AutoregressiveStrategy
        if not hasattr(scheduler, "_strategy_instances"):
            scheduler._strategy_instances = {}
            
        backend = FakeBackend()
        strategy = AutoregressiveStrategy(scheduler=scheduler, backend=backend)
        scheduler._strategy_instances[GenerationMode.AUTOREGRESSIVE] = strategy
        
        # We can test that sending an execute cycle command reaches the fake backend
        command = ExecuteCycleCommand(inputs=[])
        result = strategy.execute(command)
        
        self.assertTrue(strategy.backend.pipeline.executed)

if __name__ == "__main__":
    unittest.main()
