# Repository Audit for IMP-008

## 1. Execution Ordering Already Represented by Logical IR
The existing `ExecutionIR` currently models execution solely as a Directed Acyclic Graph (DAG) of immutable `IRNode` objects linked by `dependencies` (e.g. `node_sample` depends on `node_prefill`). This implicitly represents temporal ordering but lacks data dependencies. The current `IRBuilder` creates fixed sequences based on hardcoded execution modes ("autoregressive", "speculative", "diffusion"), which serves as the temporal execution order but is not a true compiler data-flow graph.

## 2. Duplicated Execution Sequencing
There is implicit sequence duplication embedded inside the hardcoded paths in `IRBuilder.build()`. Since nodes do not represent inputs and outputs explicitly, any backend executing these nodes would need to intrinsically know *what* data gets passed from `prefill` to `forward` to `sample`. This implies that execution sequencing logic exists both in the IR and, hypothetically, in the execution backend that would interpret the graph.

## 3. Backend-Specific Execution Assumptions
Currently, the IR nodes lack generic capability tags or operation costs, meaning the interpretation of a node like "FORWARD" carries implicit backend assumptions (e.g., that it maps directly to an MLX model forward pass). The absence of a physical lowering step forces the Logical IR to conceptually stretch all the way to backend execution, tightly coupling backend concepts (like implicit KV cache updates) to logical graph steps.

## 4. Execution Profile Dependencies
The current `ExecutionPlan` relies heavily on high-level strings like `execution_mode = "autoregressive"` or `"speculative"`, and `execution_backend = "autoregressive"`. The `IRBuilder` switches its generation logic based completely on these profile fields. This acts as a monolithic dispatch rather than assembling execution from composable capabilities and data flows.

## 5. Scheduler Assumptions
The `ExecutionPlan` dictates a `scheduler_strategy` (e.g., `"continuous_batching"`), assuming the downstream scheduler will just know how to handle the generated IR based on the mode. Because the IR lacks representation of values like `KVCache` or `TokenStream`, the scheduler is presumed to handle memory allocation, caching, and stream tracking entirely outside of the IR's purview, breaking the "compiler" abstraction.

## 6. Backend Operation Boundaries
Currently, there is no boundary between logical intent (e.g., "calculate attention") and physical execution ("run MLX kernel with Metal"). `IRNode` acts as both, which will violate abstraction once we introduce multiple backends or optimizations like speculative decoding where logical and physical structures diverge.
