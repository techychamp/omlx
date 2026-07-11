# SPDX-License-Identifier: Apache-2.0
import pytest
import concurrent.futures
from omlx.tooling.trace.tracer import CompilerTracer

def test_parallel_tracing():
    # Tracer is currently instantiated per-use in tools, so it's inherently thread-safe
    # if not shared. If shared globally, we'd need thread-locals.
    # For now, we just test that multiple instances don't collide.
    def run_trace(tracer, pass_name):
        with tracer.trace_session() as trace:
            with tracer.trace_pass(pass_name):
                pass
        return trace

    tracers = [CompilerTracer() for _ in range(5)]
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_trace, t, f"pass_{i}") for i, t in enumerate(tracers)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    assert len(results) == 5
    for r in results:
        assert len(r.timings) == 1
