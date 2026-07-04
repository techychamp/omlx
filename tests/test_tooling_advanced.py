# SPDX-License-Identifier: Apache-2.0
import pytest
from omlx.tooling.diff.differ import CompilerDiffer
from omlx.tooling.trace.tracer import CompilerTracer

def test_differ():
    differ = CompilerDiffer()
    old_data = {"a": 1, "b": 2, "c": {"x": 1}}
    new_data = {"a": 1, "b": 3, "d": 4, "c": {"x": 2}}

    diff = differ.diff_dicts(old_data, new_data)

    assert "d" in diff["added"]
    assert "c" in diff["changed"]
    assert diff["changed"]["b"] == {"from": 2, "to": 3}
    assert "a" not in diff["changed"]

def test_tracer():
    tracer = CompilerTracer()

    with tracer.trace_session() as trace:
        with tracer.trace_pass("test_pass"):
            pass # simulate work

    assert len(trace.events) == 4 # start, pass_start, pass_end, end
    assert "test_pass" in trace.timings
    assert trace.timings["test_pass"] > 0
