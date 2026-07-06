# Ownership Verification Report

Ownership domains remain cleanly separated:
1. **Device Optimization:** Owns optimization passes and optimization policies. Provides diagnostics.
2. **Compiler:** Only consumes optimized planning bundles. Never implements optimization execution policies.
3. **Execution Engine:** Consumes final Physical IR without any optimization details filtering down into dispatch logic.
4. **Runtime/Scheduler:** Purely manage state lifecycles and dependency scheduling, blind to device tuning and placement affinity overrides.
