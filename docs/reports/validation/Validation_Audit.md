# Validation Audit

- Inference entry points: `omlx.api.v1.runtime`, `omlx.api.v1.compiler`
- Model loading paths: `omlx/runtime/model_loader.py`, `omlx/runtime/model_registry.py`
- Backend execution paths: `omlx/runtime/backend_adapter.py`, `omlx/runtime/execution_engine.py`
- Runtime execution paths: `omlx/runtime/compiler_service.py`, `omlx/runtime/execution_engine.py`
- Feature flags: Located in `omlx/runtime/feature_flags.py`
- Compiler outputs: ModelDescriptor, CapabilityDescriptor, ExecutionPlan, LogicalIR, PhysicalIR, BackendOperationGraph, ExecutionSchedule
