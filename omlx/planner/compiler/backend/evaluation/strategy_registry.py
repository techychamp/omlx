import threading
from typing import Mapping

# Dummy stub for strategy base class. We will adapt this if we find an existing protocol
from ..selection.policy import PolicyStrategy

BackendSelectionStrategy = PolicyStrategy

class BackendPolicyStrategyRegistry:
    """Registry for backend selection strategies."""
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._strategies: dict[str, BackendSelectionStrategy] = {}
        self._is_locked = False

        # Auto-register default strategies
        from ..selection.policy import BackendSelectionPolicy, get_policy_strategy
        for policy in BackendSelectionPolicy:
            self._strategies[policy.name] = get_policy_strategy(policy)

    def register(self, strategy_id: str, strategy: BackendSelectionStrategy) -> None:
        """Register a new strategy."""
        with self._lock:
            if self._is_locked:
                raise RuntimeError("Registry is locked. Cannot register new strategies.")
            self._strategies[strategy_id] = strategy

    def unregister(self, strategy_id: str) -> None:
        """Unregister an existing strategy before the registry is locked."""
        with self._lock:
            if self._is_locked:
                raise RuntimeError("Registry is locked. Cannot unregister strategies.")
            if strategy_id in self._strategies:
                del self._strategies[strategy_id]

    def get(self, strategy_id: str) -> BackendSelectionStrategy:
        """Query a strategy by ID."""
        with self._lock:
            if strategy_id not in self._strategies:
                raise KeyError(f"Strategy {strategy_id} not found.")
            return self._strategies[strategy_id]

    def resolve(self, strategy_id: str) -> BackendSelectionStrategy:
        """Alias for `get`."""
        return self.get(strategy_id)

    def lock(self) -> None:
        """Lock the registry, making it immutable."""
        with self._lock:
            self._is_locked = True
