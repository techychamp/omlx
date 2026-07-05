# SPDX-License-Identifier: Apache-2.0
"""
Compiler Tracer
Provides read-only tracing for compiler passes and timing.
"""
import time
from contextlib import contextmanager
from typing import Any

class CompilerTrace:
    """Stores trace data."""
    def __init__(self):
        self.events = []
        self.timings = {}
        self.diagnostics = []

    def record_event(self, name: str, data: dict[str, Any] = None):
        self.events.append({"event": name, "data": data or {}, "timestamp": time.time()})

    def add_diagnostic(self, msg: str):
        self.diagnostics.append({"msg": msg, "timestamp": time.time()})

class CompilerTracer:
    """Manages compiler traces thread-locally or globally for debugging."""
    def __init__(self):
        self.current_trace = None

    @contextmanager
    def trace_session(self):
        """Context manager to start and stop a tracing session."""
        self.current_trace = CompilerTrace()
        self.current_trace.record_event("session_start")
        try:
            yield self.current_trace
        finally:
            self.current_trace.record_event("session_end")

    @contextmanager
    def trace_pass(self, pass_name: str):
        """Times and records a compiler pass."""
        start = time.perf_counter()
        if self.current_trace:
            self.current_trace.record_event(f"pass_start_{pass_name}")

        try:
            yield
        finally:
            duration = time.perf_counter() - start
            if self.current_trace:
                self.current_trace.record_event(f"pass_end_{pass_name}", {"duration_sec": duration})
                self.current_trace.timings[pass_name] = duration

class InteractiveTrace(CompilerTrace):
    """Extends CompilerTrace with export formatters."""

    def export_markdown(self) -> str:
        """Exports the trace timeline as Markdown."""
        lines = ["# Compiler Trace Timeline\n"]
        for evt in self.events:
            lines.append(f"- **{evt['timestamp']}**: {evt['event']} (Data: {evt['data']})")
        if self.diagnostics:
            lines.append("\n## Diagnostics\n")
            for diag in self.diagnostics:
                lines.append(f"- {diag['msg']}")
        return "\n".join(lines)

    def export_mermaid(self) -> str:
        """Exports the trace timeline as a Mermaid Gantt chart."""
        lines = ["gantt", "    title Compiler Trace Timeline", "    dateFormat  X", "    axisFormat %s"]

        # very simple mapping
        for idx, evt in enumerate(self.events):
            # Using index as a proxy for time for simple visualization
            lines.append(f"    {evt['event']} : {idx}, 1d")

        return "\n".join(lines)
