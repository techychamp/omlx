# Backend Negotiation Walkthrough

## Overview
The Backend Capability Negotiation framework ensures that before a backend is selected, a structured conversation occurs between the requested `ExecutionPlan`, the `CapabilityDescriptor` (what the model needs), and the `BackendDescriptor` (what the hardware/software can do).

## Negotiation Points
1. **Execution Family**: Does the backend support the execution family (e.g. Causal LM, VLM)?
2. **Attention Support**: Does the backend support the specific attention type (e.g. SDPA, Paged)?
3. **Streaming**: Does the backend support real-time token streaming if required?
4. **MoE Routing**: Are expert routing rules supported if the model is a Mixture of Experts?

## Outcome
The negotiation phase results in a `NegotiationDiagnostics` object. This object holds booleans indicating which capabilities matched. The `CompatibilityChecker` will then use these to make a hard decision, while the `BackendSelectionFramework` uses it to populate evaluation diagnostics for tooling.
