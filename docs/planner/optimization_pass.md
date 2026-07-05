# Optimization Pass Architecture

Optimization Passes allow developers to implement discrete, reusable rules for plan modification without bloating the core `ExecutionPlanner`.

### `PlanningPass` Protocol

A valid pass must implement the `PlanningPass` protocol:

```python
class PlanningPass(Protocol):
    @property
    def name(self) -> str: ...

    def apply(self, plan: dict, capability_descriptor: CapabilityDescriptor) -> None: ...
```

### Flow

During the `ExecutionPlanner.plan()` flow, passes are retrieved from the `PassRegistry`. Each pass receives a *mutable dictionary* representing the pending plan, and the immutable `CapabilityDescriptor`.

Passes can modify `execution_hints`, adjust the `scheduler_strategy`, or change `execution_backend` logic prior to the dictionary being frozen into an `ExecutionPlan`.
