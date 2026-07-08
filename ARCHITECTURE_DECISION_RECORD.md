# Architecture Decision Record

Decision: Compiler transforms MemoryPlan to ExecutionIR. Reason: Keeps Runtime and Execution clean of domain-specific logic, maintaining deterministic parallel scheduling.
