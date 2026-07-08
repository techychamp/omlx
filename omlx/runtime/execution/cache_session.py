# SPDX-License-Identifier: Apache-2.0
"""
Runtime cache session coordination.
"""

class CacheSession:
    """
    Coordinates cache lifecycle attached to an execution session.
    Managed by the Runtime, but does not implement cache logic.
    """
    def __init__(self, cache_plan=None):
        self._cache_plan = cache_plan
        self._is_active = False

    @property
    def cache_plan(self):
        return self._cache_plan

    def activate(self):
        self._is_active = True

    def deactivate(self):
        self._is_active = False

    def is_active(self) -> bool:
        return self._is_active
