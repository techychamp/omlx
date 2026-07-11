# Tooling Audit

## Missing Developer Workflows
- **Compiler Replay:** No ability to capture and deterministically replay the compiler pipeline offline.
- **Artifact Exploration:** No ability to navigate the relationships between artifacts (CapabilityDescriptor -> ExecutionPlan -> Logical IR -> Physical IR -> Backend Graph).

## Missing Inspection Features
- **Semantic Inspection:** Current inspector only understands structural representations (dicts/graphs). It lacks semantic understanding (e.g. streaming mode, cache strategy, MoE routing).

## Missing Replay Capabilities
- Need `ReplaySession` and `CompilerSession` to bundle traces, feature flags, backends, and artifacts into portable formats.

## Missing Semantic Debugging
- Diff engine only highlights structural changes. Needs to highlight semantic changes (e.g. "Attention implementation changed").

## Missing Visualization
- Graphs lack semantic labels like `is_streaming` or cache properties.
