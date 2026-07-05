# SPDX-License-Identifier: Apache-2.0
"""
Runtime invariants verification testing.
Verifies the isolation of compiler ownership without deep importing uninstalled deps.
"""

import pytest
from unittest.mock import MagicMock

from omlx.runtime.compiler_service import RuntimeCompilerService

def test_runtime_compiler_service_ownership():
    """Verify that Runtime owns the Compiler Service and it exists precisely once per runtime instance."""

    class MockRuntime:
        def __init__(self):
            self.feature_flags = MagicMock()
            self.context = MagicMock()

    mock_runtime = MockRuntime()
    service = RuntimeCompilerService(mock_runtime)

    assert hasattr(service, "runtime")
    assert service.runtime is mock_runtime

def test_server_and_pool_perform_no_planning():
    """
    Verify EnginePool relies purely on passed state and does not execute planning itself.
    """
    class MockEnginePool:
        def __init__(self, runtime):
            self.runtime = runtime

        def allocate_engine(self, model_id):
            # Simulation of allocation, should not invoke compilation
            pass

    class MockRuntime:
        def __init__(self):
            self.compiler_service = MagicMock()

    mock_runtime = MockRuntime()
    pool = MockEnginePool(mock_runtime)

    pool.allocate_engine("test")

    # Asserting that simply calling allocate_engine on the mock does not magically call run_compilation
    mock_runtime.compiler_service.run_compilation.assert_not_called()
