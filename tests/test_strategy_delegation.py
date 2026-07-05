# SPDX-License-Identifier: Apache-2.0
"""
Tests for capability-driven strategy resolution and scheduler binding.
"""

import ast
import pytest
from unittest.mock import patch

from omlx.engine_core import EngineCore
from omlx.scheduler import Scheduler
from omlx.inference.strategies.autoregressive import AutoregressiveStrategy
from omlx.inference.backends.autoregressive_backend import AutoregressiveBackend


def test_scheduler_static_invariants():
    """Statically verify that omlx/scheduler.py does not import or reference registries."""
    with open("omlx/scheduler.py", "r") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [alias.name for alias in node.names]
            for name in names:
                assert "GenerationStrategyRegistry" not in name, (
                    "Scheduler must not import GenerationStrategyRegistry"
                )
                assert "CapabilityRegistry" not in name, (
                    "Scheduler must not import CapabilityRegistry"
                )
                assert "ExecutionProfileRegistry" not in name, (
                    "Scheduler must not import ExecutionProfileRegistry"
                )
        # Check variable or identifier references
        if isinstance(node, ast.Name):
            assert node.id != "GenerationStrategyRegistry", (
                "Scheduler must not reference GenerationStrategyRegistry"
            )
            assert node.id != "CapabilityRegistry", (
                "Scheduler must not reference CapabilityRegistry"
            )
            assert node.id != "ExecutionProfileRegistry", (
                "Scheduler must not reference ExecutionProfileRegistry"
            )


def test_engine_core_resolves_and_binds_strategy(mock_model, mock_tokenizer):
    """Dynamically verify EngineCore resolves and binds AutoregressiveStrategy to the Scheduler."""
    with patch("omlx.engine_core.get_registry") as mock_registry:
        mock_registry.return_value.acquire.return_value = True

        engine = EngineCore(model=mock_model, tokenizer=mock_tokenizer)
        try:
            # 1. Assert scheduler has a strategy
            assert engine.scheduler.strategy is not None, "Strategy was not injected into Scheduler"
            
            # 2. Assert the strategy is AutoregressiveStrategy
            assert isinstance(engine.scheduler.strategy, AutoregressiveStrategy), (
                f"Expected AutoregressiveStrategy, got {type(engine.scheduler.strategy)}"
            )
            
            # 3. Assert the strategy is correctly bound to the scheduler and backend
            assert engine.scheduler.strategy.scheduler is engine.scheduler, (
                "Strategy scheduler reference mismatch"
            )
            assert isinstance(engine.scheduler.strategy.backend, AutoregressiveBackend), (
                "Strategy is not bound to AutoregressiveBackend"
            )
        finally:
            engine.close()
