# Backend Scoring Framework
The `BackendScoringFramework` provides a stateless calculation mechanism to yield a comparative `BackendScore`. It evaluates a `BackendDescriptor`, the `PhysicalIR`, and `ExecutionConstraints` to score a backend across multiple dimensions (latency, memory, throughput, compatibility). It does not select a backend; selection occurs in the Runtime Planner.
