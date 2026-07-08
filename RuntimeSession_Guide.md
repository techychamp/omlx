# RuntimeSession Guide

`RuntimeSession` serves as the primary artifact orchestrating intent lifecycle. Use `session.transition(SessionState)` to alter state cleanly. Do not mutate underlying `ExecutionContext` artifacts.