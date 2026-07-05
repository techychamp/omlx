# SPDX-License-Identifier: Apache-2.0
"""
Artifacts for OMLX Execution Engine.
"""

from typing import Any

# Re-export or stub BackendOperationGraph for the execution engine to depend on
# Ideally this comes from the compiler backend package, but we create an alias/type hint here
BackendOperationGraph = Any
