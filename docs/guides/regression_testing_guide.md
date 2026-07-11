# Regression Testing Guide

The regression infrastructure exists to rapidly build and register regression test suites without reinventing fixtures.

## Key Supported Regression Modes
- **Unit Regression**: Component-level assertions against known bugs.
- **Integration Regression**: Full system workflows to detect pipeline breakdown.
- **Compiler Regression**: Verification that the Compiler generates the correct sequence of execution phases.
- **Backend Regression**: Assertions on the operation graph translation and operation ordering.
- **Runtime Regression**: Execution environment checks and state transitions.
- **API & CLI Regression**: Validation of the developer experience interface.

## Registering a Suite
Future developers must place regression tests in `tests/verification/regression/` utilizing the base regression fixtures provided by `tests/verification/framework/`.
