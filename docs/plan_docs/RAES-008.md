# RAES-008: Runtime Capability Registry & Capability Resolution

## 1. Repository Audit

A comprehensive audit of the codebase has been conducted to locate where execution decisions, backend selection, and capability inferences are currently hardcoded.

### Hardcoded Locations Identified
- **`omlx/runtime/capabilities.py`**:
  - `ModelCapabilities`, `EngineCapabilities`, and `ActualCapabilities` are static dataclasses with hardcoded boolean flags (`supports_diffusion`, `supports_linear_speculation`, etc.).
  - `ActualCapabilities.resolve` uses manual, hardcoded `and` combinations to intersect model, engine, and feature flags.
  - `infer_capabilities` relies on hardcoded string matching (`if "diffusion" in model_type or model_type == "nemotron_labs_diffusion":`).
- **`omlx/inference/execution_profile.py`**:
  - `_default_resolver` contains hardcoded mapping from model types to backend profiles.
  - `ExecutionProfileRegistry.resolve` contains hardcoded capability negotiation (fallback logic from diffusion/linear_speculation to autoregressive).
  - Backend factories (`_autoregressive_factory`, `_experimental_nemotron_factory`) are hardcoded at module initialization.
- **`omlx/registry/model_info.py`**:
  - `build_model_info` contains static, hardcoded logic for setting modes and attention types based on specific capability boolean flags.
- **`omlx/registry/capability_registry.py`**:
  - `GenerationStrategyRegistry.resolve_mode` applies hardcoded fallback logic.
  - `register_default_strategies` is hardcoded.
- **`omlx/engine_core.py`**:
  - Combines capabilities, configures the context, resolves the execution profile, and builds the strategy registry inline.

## 2. Architecture Review

The current architecture is highly coupled to specific generation modes via boolean fields and `if/else` statements.

**Goal**: Move to a declarative registry where capabilities are registered, discovered, and resolved via a generic `ResolutionEngine`. This insulates core components from execution logic and establishes a clean, cohesive abstraction chain:

```text
Model Discovery
        │
        ▼
Model Adapter          (RAES-010)
        │
        ▼
Capability Registry    (RAES-008)
        │
        ▼
Capability Resolver
        │
        ▼
Execution Planner
        │
        ▼
Execution Graph        (RAES-011)
        │
        ▼
Optimization Passes
        │
        ▼
Generation Strategy
        │
        ▼
Execution Backend
        │
        ▼
Execution Engine
        │
        ▼
MLX Runtime
```

## 3. Capability Descriptor Design

The registry will handle dynamic registration of capabilities using a nested `CapabilityDescriptor`. Rather than a flat list of boolean fields, capabilities describe execution characteristics in isolated concern domains.

Capabilities are divided into two distinct domains:

### 3.1. Static Capabilities
Declared by the model itself, these never change.
- `supports_diffusion`, `supports_vision`, `supports_MoE`
- `attention_type` (causal, bidirectional)

### 3.2. Runtime Capabilities
Resolved dynamically per-execution based on the environment and request.
- `metal_available`, `memory_limits`, `batch_size`
- `cache_implementation`, `execution_mode`, `verification_enabled`

### 3.3. The Descriptor
To keep each concern isolated, `CapabilityDescriptor` is composed of sub-descriptors:

```python
@dataclass
class VerificationDescriptor:
    verification_passes: list[str]

@dataclass
class ExecutionDescriptor:
    execution_family: str
    attention_type: str
    cache_type: str
    scheduler_hints: list[str]
    execution_graph: str
    backend: str
    pipeline: str
    engine: str
    adapter: str

@dataclass
class HardwareDescriptor:
    required_memory: int
    required_backend: list[str]

@dataclass
class UISchemaDescriptor:
    display_name: str
    description: str

@dataclass
class CapabilityDescriptor:
    id: str
    family: str  # e.g., "architecture", "execution", "hardware", "verification", "scheduling"

    ui: UISchemaDescriptor
    execution: ExecutionDescriptor
    hardware: HardwareDescriptor
    verification: VerificationDescriptor | None

    dependencies: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    inherits_from: str | None = None
    priority: int = 0
```

## 4. Capability Families, Composition, & Inheritance

Instead of one flat registry, capabilities are organized into **Capability Families** to remain manageable as the system grows:
* Architecture
* Execution
* Hardware
* Verification
* Scheduling
* Memory
* Streaming
* Plugins

### Capability Inheritance
The registry supports inheritance to define hierarchical capabilities without duplicating base descriptors:
```text
Transformer -> Autoregressive -> Speculative -> Triage
```

### Capability Composition
The `CapabilityResolver` composes fundamental capabilities into Composite Capabilities at runtime, avoiding an explosion of registered permutations.

Example: Streaming MoE
```text
Transformer + Streaming + MoE  ->  Streaming MoE Runtime
```

## 5. Resolution Engine & Environment Design

### 5.1 Immutable Execution Environment
The `ExecutionEnvironment` must be an immutable snapshot generated at startup. Nothing modifies it during runtime.
```python
@dataclass(frozen=True)
class ExecutionEnvironment:
    mlx_version: str
    metal_version: str
    ram_gb: int
    gpu_type: str
    cpu_arch: str
    os_version: str
    drivers: list[str]
```

### 5.2 Lazy Evaluation
Some capabilities (e.g. memory limits, custom kernels, external plugins) can be expensive to compute. The registry should support **lazy evaluation** mechanisms, allowing capabilities to provide a factory/callback that is only evaluated during resolution, rather than at startup time.

### 5.3 Resolution Flow
The `CapabilityResolver` composes and resolves runtime components dynamically. The **`ExecutionPlanner` is the ONLY consumer of resolved capabilities**. No backend, engine, or scheduler should inspect capabilities directly.

**Process**:
1. Query registries across all Capability Families.
2. Filter capabilities against the immutable `ExecutionEnvironment` snapshot.
3. Resolve dependencies, remove conflicts (topological sort), and flatten inheritance chains. (Support lazy evaluations here).
4. Perform Capability Composition.
5. Output the resolved `CompositeCapability` to the `ExecutionPlanner`.
6. `ExecutionPlanner` consumes the resolved capabilities and emits an `ExecutionGraph`.

## 6. Diagrams

### 6.1. Registry Relationships
```mermaid
classDiagram
    class CapabilityRegistry {
        +register(cap: CapabilityDescriptor)
        +get_all() -> List[CapabilityDescriptor]
        +get_by_id(id: str) -> CapabilityDescriptor
    }
    class ExecutionEnvironment {
        +mlx_version: str
        +metal_version: str
        +ram_gb: int
    }
    class CapabilityResolver {
        +resolve(model_info, environment, overrides) -> CompositeCapability
    }
    class ExecutionPlanner {
        +plan(caps: CompositeCapability) -> ExecutionGraph
    }
    class ExecutionGraph {
        +nodes: List[ExecutionNode]
    }
    CapabilityResolver --> CapabilityRegistry : Queries Families
    CapabilityResolver --> ExecutionEnvironment : Checks hardware/OS limits
    CapabilityResolver --> ExecutionPlanner : Outputs CompositeCapability
    ExecutionPlanner --> ExecutionGraph : Outputs
```

### 6.2. Initialization Flow
```mermaid
sequenceDiagram
    participant EngineCore
    participant Resolver as CapabilityResolver
    participant Registry as CapabilityRegistry
    participant Planner as ExecutionPlanner

    EngineCore->>EngineCore: generate ExecutionEnvironment snapshot
    EngineCore->>Resolver: resolve(model_static_caps, env_snapshot, flags)
    Resolver->>Registry: get_matching_capabilities()
    Registry-->>Resolver: List[CapabilityDescriptor] (Lazy Evaluation)
    Resolver->>Resolver: resolve inheritance & compose capabilities
    Resolver->>Resolver: resolve dependencies & conflicts
    Resolver-->>EngineCore: CompositeCapability
    EngineCore->>Planner: generate_plan(composite_capability)
    Planner-->>EngineCore: ExecutionGraph
```

## 7. Files To Modify

- **NEW `omlx/runtime/capability_registry.py`**: Defines nested descriptors (`CapabilityDescriptor`, `ExecutionDescriptor`, etc.) and family-partitioned registries.
- **NEW `omlx/runtime/resolver.py`**: Implements the `CapabilityResolver` (lazy evaluation, static vs runtime composition, inheritance).
- **NEW `omlx/runtime/environment.py`**: Defines the immutable `ExecutionEnvironment` snapshot.
- **MODIFIED `omlx/runtime/capabilities.py`**: Deprecate hardcoded boolean dataclasses in favor of dynamic resolution.
- **MODIFIED `omlx/inference/execution_profile.py`**: Retained/modified as part of the `ExecutionPlanner`'s output, removing old fallback logic.
- **MODIFIED `omlx/registry/model_info.py`**: Remove hardcoded capability checks.
- **MODIFIED `omlx/engine_core.py`**: Update initialization to use the new `CapabilityResolver` -> `ExecutionPlanner` pipeline.

## 8. What This Enables Later

Once this exists, adding a completely new execution family becomes much simpler and highly extensible.

For example, suppose we add **Nemotron Triage**.
- You don't change the scheduler.
- You don't change the backend.
- You simply register new capability descriptors:
  - Architecture: `Transformer`
  - Execution: `Verification`
  - Scheduling: `Draft Verify`
  - Memory: `Paged Cache`

The resolver composes them automatically. The planner builds an appropriate execution graph. The runtime executes it seamlessly.

## 9. Risk Analysis

- **Cyclic Dependencies**: Capability inheritance or dependencies could create cycles (e.g., A depends on B, B depends on A). The `CapabilityResolver` must implement topological sorting and cycle detection to fail fast during resolution.
- **Startup Latency**: Dynamically resolving capabilities could increase initialization time. We mitigate this through **lazy evaluation** and caching resolver results per `model_info` configuration.
- **Registration Ordering**: If plugins or capabilities are registered in non-deterministic orders, resolution could fail. The registry must enforce lazy resolution (evaluate after all registrations are complete).
- **Future Compatibility**: Modifying `EngineCore` logic might break external tools using older SDKs. The resolved structures should expose legacy properties as computed properties to maintain backwards compatibility in the short term.
- **Verification Implications**: Testing combinatorial capabilities requires exponential test cases. We must rely on `VerificationDescriptor` passes to test the most common composed capabilities rather than enumerating all permutations.

## 10. Verification Plan

1. **Family Registration**: Verify capabilities can be registered under specific families (Architecture, Execution, Streaming, etc.).
2. **Inheritance & Composition Correctness**: Tests to verify capability inheritance (Autoregressive inherits from Transformer) and composition (Transformer + Streaming + MoE correctly synthesizes into a composite descriptor).
3. **Static vs Runtime Separation**: Ensure static capabilities from the model dictate which runtime capabilities can be composed.
4. **Environment Resolution**: Verify the immutable `ExecutionEnvironment` correctly restricts capabilities based on MLX version, memory, and custom kernels.
5. **Lazy Evaluation**: Ensure that expensive capability callbacks are only invoked when required during the resolution phase.
6. **Execution Planner Consumes Capabilities**: Validate that the resolved capability descriptor successfully maps to a planned `ExecutionGraph` and that no other component inspects capabilities.

## 11. Rollback Plan

- **Version Control**: Work will be done in a feature branch.
- **Feature Flag**: Introduce a feature flag `OMLX_USE_NEW_RESOLVER` (default to False initially) to allow side-by-side execution if needed.
- **Reversion**: If the new resolver causes regressions, toggle the flag or revert the branch.

## 12. Recommendation for the Implementation Checkpoint

We recommend proceeding with **RAES-008 Checkpoint 1: Capability Registry & Environment Foundation**:
* **Goal**: Implement `CapabilityDescriptor` (with nested descriptors), the immutable `ExecutionEnvironment`, and the partitioned `CapabilityRegistry`.
* **Purpose**: Establish the core data structures and ensure they can resolve inheritance, dependencies, conflicts, lazy evaluations, and basic composition through tests.
* **Allowed Files**: `omlx/runtime/capability_registry.py`, `omlx/runtime/resolver.py`, `omlx/runtime/environment.py`, `tests/test_capability_registry.py`.
* **Forbidden Files**: `omlx/engine_core.py`, `omlx/scheduler.py`.
* **Exit Criteria**: Registry, immutable environment detection, lazy evaluation, and resolver logic is implemented and passes unit tests covering inheritance, composition, and static/runtime boundaries.
