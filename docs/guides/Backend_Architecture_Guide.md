# Backend Architecture Guide

## Overview
This document outlines the architectural boundaries and responsibilities for the OMLX execution backend, particularly focusing on the MLX integration introduced in BACKEND-005.

## Core Architectural Rules
- **Runtime owns orchestration.** The runtime coordinates the high-level flow of compilation and execution.
- **ExecutionEngine owns execution flow.** It manages the graph executor and overall progress through the execution schedule.
- **GraphScheduler owns execution order.** It determines the sequence in which operations are dispatched.
- **ExecutionDispatcher owns dispatch.** It takes the schedule and dispatches individual operations to the adapter.
- **BackendAdapter owns backend operation execution.** The adapter is solely responsible for translating and executing physical IR operations on the target hardware (e.g., Apple Silicon via MLX).

## Backend Limitations (By Design)
The backend MUST NOT own:
- Text generation logic
- Token sampling and decode loops
- Speculative execution coordination
- Global runtime state

These responsibilities remain within the Runtime layer. For example, token sampling is handled by a separate component in the runtime, which interprets the logits produced by the backend's forward pass.

## Execution Flow Example
1. `ExecutionDispatcher` calls `MLXAdapter.execute(operation, context)`.
2. `MLXAdapter.execute` inspects the `operation` type.
3. For an `MLXForwardOperation`, it retrieves the lightweight model reference from `ExecutionContext.model`.
4. The adapter extracts input dependencies (e.g., `input_ids`) from `ExecutionContext.request_context`.
5. The adapter performs a real forward kernel dispatch using `context.model(input_ids)`.
6. The resulting logits are returned in the execution result to the dispatcher.

## Thread Safety and State Management
- `MLXAdapter` is completely stateless. It does not store models or tokenizer objects as instance attributes.
- All required state for a kernel dispatch is passed explicitly via the `ExecutionContext`.
- This ensures execution remains thread-safe and allows multiple execution streams or requests to be processed concurrently without synchronization conflicts on the backend itself.
