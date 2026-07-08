#!/bin/bash
# Pre-commit step
echo "Running pre-commit checks..."
PYTHONPATH=. pytest tests/runtime/execution/test_moe_execution.py
