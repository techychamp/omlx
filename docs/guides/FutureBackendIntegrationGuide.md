# Future Backend Integration Guide

To implement a new backend (e.g. `CUDAAdapter`):
1. Create a class inheriting `BaseBackendAdapter`.
2. Define a `BackendDescriptor` emphasizing the topology (e.g., memory_model="discrete", device_topology="multi_gpu").
3. Define the set of `BackendCapability` the hardware/framework supports.
4. Implement `validate(PhysicalIR)` to return a structured `BackendValidationResult`.
5. Implement `translate(PhysicalIR)` to return a `TranslationResult` containing backend-specific operation subclasses derived from `ReferenceBackendOperation`.
