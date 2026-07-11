# Developer Workbench Guide

## Introduction
The Developer Workbench is a centralized layer for inspecting the OMLX platform. It consumes public APIs (`omlx.api.v1`) to provide insights into Runtime, Compiler, Planning, Diagnostics, and Plugins.

## Architecture
The Workbench operates entirely out of the platform's core loops. It does not control execution, compiling, or planning. Its primary role is observability.

- `omlx.workbench.navigation.NavigationManager`: Handles routing between modules.
- `omlx.workbench.modules.*`: Implementations of different inspection screens.
- `omlx.workbench.app.DeveloperWorkbench`: The main application entry point.

## Adding a Module
1. Create a class inheriting from `WorkbenchModule`.
2. Define `ModuleInfo`.
3. Register the module using `navigation.register_module(module)`.

## Thread Safety
The Workbench uses threading locks where necessary (e.g., when initializing modules) to ensure thread-safe concurrent views of the OMLX backend.

## Integration
The Workbench can be extended into a fully featured Web GUI without requiring structural changes to OMLX.
