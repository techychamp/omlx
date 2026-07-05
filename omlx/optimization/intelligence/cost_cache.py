# SPDX-License-Identifier: Apache-2.0
"""
Cost Cache extending the base CompilerCache to cache cost estimates,
analysis results, and profitability analysis.
"""
from typing import Optional, Any
from omlx.compiler_perf.cache import CompilerCache

class CostCache(CompilerCache):
    def __init__(self, **kwargs):
        super().__init__(name="cost_cache", **kwargs)

    def get_estimate(self, key: str) -> Optional[Any]:
        return self.get(f"estimate:{key}")

    def put_estimate(self, key: str, estimate: Any) -> None:
        self.put(f"estimate:{key}", estimate)

    def get_analysis(self, key: str) -> Optional[Any]:
        return self.get(f"analysis:{key}")

    def put_analysis(self, key: str, analysis: Any) -> None:
        self.put(f"analysis:{key}", analysis)

    def get_profitability(self, key: str) -> Optional[Any]:
        return self.get(f"profitability:{key}")

    def put_profitability(self, key: str, profitability: Any) -> None:
        self.put(f"profitability:{key}", profitability)
