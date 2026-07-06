import re

with open("tests/test_execution_engine.py", "w") as f:
    f.write("""# SPDX-License-Identifier: Apache-2.0
\"\"\"
Tests for TransformerExecutionEngine.
\"\"\"

from unittest.mock import MagicMock
import pytest

from omlx.request import SamplingParams
from omlx.inference.execution_engine import TransformerExecutionEngine

def test_transformer_execution_engine_initial_state():
    engine = TransformerExecutionEngine(batch_generator=None)
    assert engine.has_generator()  # Now defaults to true for native compiler

    with pytest.raises(NotImplementedError):
        engine.forward()

    assert engine.eval_cache() == 0
    assert engine.extract_cache(42) is None

def test_transformer_execution_engine_delegation():
    engine = TransformerExecutionEngine(batch_generator=None)
    assert engine.has_generator()

    # Test new compiler native mocks
    uids = engine.insert(tokens=[1])
    assert uids == [0]

    engine.remove([0])

    res = engine.extract_cache([0])
    assert res is None

    with pytest.raises(NotImplementedError):
        list(engine.forward())
""")
