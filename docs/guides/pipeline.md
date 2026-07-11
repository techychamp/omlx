# Planning Pipeline Documentation

The planning pipeline executes in multiple distinct phases within `ExecutionPlanner.plan()`:

1. **Base Plan Construction**: Extracts direct mappings from the `CapabilityDescriptor` (e.g., Execution Family).
2. **Execution Strategy Selection**: Determines the specific backend (`_select_backend`) and execution mode (`_select_mode`) based on capabilities like `supports_speculative` or `supports_streaming`.
3. **Optimization Passes**: Iterates through the injected `PassRegistry` and applies each `PlanningPass`.
4. **Finalization & Timing**: Records planning latency and freezes the dictionary into an `ExecutionPlan` dataclass.
5. **Validation**: Passes the frozen plan to `validate_plan` to ensure structural integrity and logical consistency.
