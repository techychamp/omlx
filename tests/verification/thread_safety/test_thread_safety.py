# SPDX-License-Identifier: Apache-2.0
"""
Thread Safety verification testing.
Verifies that multi-threaded access to RuntimeCompilerService behaves correctly without race conditions.
"""

import pytest
import concurrent.futures
from unittest.mock import MagicMock

from omlx.runtime.compiler_service import RuntimeCompilerService

def test_compiler_service_thread_safety():
    """Verify that concurrent compilation requests do not corrupt statistics or crash."""
    mock_runtime = MagicMock()
    mock_runtime.feature_flags.COMPILER_RUNTIME_PIPELINE_ENABLED = True
    mock_runtime.feature_flags.COMPILER_CONTEXT_ENABLED = False

    # Let's bypass the actual complex logic by mocking runner
    service = RuntimeCompilerService(mock_runtime)
    service._runner = MagicMock()
    service._runner.run_pipeline.return_value = MagicMock() # Simulate a successful result

    num_threads = 50
    requests_per_thread = 10
    total_requests = num_threads * requests_per_thread

    def worker():
        for _ in range(requests_per_thread):
            service.run_compilation("concurrent_model")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        concurrent.futures.wait(futures)

    # Validate statistics have not race-conditioned
    stats = service.statistics
    assert stats["total_compilations"] == total_requests
    assert stats["successful_compilations"] == total_requests
    assert stats["failed_compilations"] == 0
