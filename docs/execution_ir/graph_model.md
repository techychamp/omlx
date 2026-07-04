# Execution IR Graph Model

## Graph
The ExecutionIR is represented as an instance of the `ExecutionIR` class, which holds:
- `nodes`: A dictionary mapping node IDs to `IRNode` instances.
- `roots`: A tuple of root node IDs.

## Nodes
Each step in the DAG is an `IRNode`.
Nodes have:
- `id`: Unique identifier
- `node_type`: From `IRNodeType` enum (Prefill, Forward, Sample, Verify, Emit, etc.)
- `dependencies`: Tuple of node IDs that this node depends on.
- `metadata`: Immutable key-value map for diagnostics, execution hints, etc.

## Extensibility
Future graph node categories are simply added to the `IRNodeType` enum. The design handles arbitrary node topologies for speculative and diffusion generation without changing the core graph logic.
