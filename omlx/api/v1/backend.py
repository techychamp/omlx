from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
from omlx.planner.compiler.backend.registry import AdapterRegistry
from omlx.api.v1.exceptions import BackendError

class HardwareConstraint(BaseModel, frozen=True):
    constraint_type: str
    value: Any
    is_hard_requirement: bool = True

class BackendSelectionResult(BaseModel, frozen=True):
    selected_backend: str
    score: float
    reason: str
    fallback_chain: List[str] = Field(default_factory=list)
    capabilities_supported: List[str] = Field(default_factory=list)
    diagnostics: Dict[str, str] = Field(default_factory=dict)

class BackendRequest(BaseModel, frozen=True):
    model_family: str
    hardware_constraints: List[HardwareConstraint] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)

class BackendManager:
    def __init__(self):
        self._registry = AdapterRegistry()

    async def select_backend_async(self, request: BackendRequest) -> BackendSelectionResult:
        return await asyncio.to_thread(self.select_backend, request)

    def select_backend(self, request: BackendRequest) -> BackendSelectionResult:
        try:
            # Query the adapter registry based on requested model family/capabilities
            # In a full implementation, we'd use a BackendSelectionPolicy. Here we mock the behavior
            # based on if a matching adapter exists for standard fallback logic.

            adapters = self._registry.query()
            selected = "mlx"
            reason = "Default fallback"

            if len(adapters) > 0:
                selected = adapters[0].backend
                reason = "Matched from registry query"

            return BackendSelectionResult(
                selected_backend=selected,
                score=1.0,
                reason=reason,
                fallback_chain=["mlx"]
            )
        except Exception as e:
            raise BackendError(f"Backend selection failed: {str(e)}") from e

class BackendRequestBuilder:
    def __init__(self):
        self._model_family: str = "llama"
        self._constraints: List[HardwareConstraint] = []
        self._required_capabilities: List[str] = []

    def with_model_family(self, family: str) -> 'BackendRequestBuilder':
        self._model_family = family
        return self

    def with_constraint(self, key: str, value: Any, hard: bool = True) -> 'BackendRequestBuilder':
        self._constraints.append(HardwareConstraint(constraint_type=key, value=value, is_hard_requirement=hard))
        return self

    def require_capability(self, capability: str) -> 'BackendRequestBuilder':
        self._required_capabilities.append(capability)
        return self

    def build_request(self) -> BackendRequest:
        return BackendRequest(
            model_family=self._model_family,
            hardware_constraints=self._constraints,
            required_capabilities=self._required_capabilities
        )

    def build(self) -> BackendManager:
        return BackendManager()
