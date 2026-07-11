# Tracing Guide

Tracing is accomplished using the `TraceBuilder` inside `Observer`. Wrap phases using `with observer.observe_phase('phase_name', 'component', 'operation'):`.