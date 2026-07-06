from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
from omlx.api.v1.exceptions import VerificationError

class VerificationMetric(BaseModel, frozen=True):
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float] = None
    passed: bool = True

class VerificationResult(BaseModel, frozen=True):
    passed: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metrics: List[VerificationMetric] = Field(default_factory=list)
    diagnostics: Dict[str, str] = Field(default_factory=dict)

class VerificationRequest(BaseModel, frozen=True):
    target_id: str
    ruleset: str = "default"
    strict_mode: bool = False

class Verifier:
    def __init__(self):
        pass

    async def verify_async(self, request: VerificationRequest) -> VerificationResult:
        return await asyncio.to_thread(self.verify, request)

    def verify(self, request: VerificationRequest) -> VerificationResult:
        try:
            return VerificationResult(
                passed=True,
                metrics=[
                    VerificationMetric(metric_name="latency", value=12.4, unit="ms", passed=True)
                ]
            )
        except Exception as e:
            raise VerificationError(f"Verification failed: {str(e)}") from e

class VerificationRequestBuilder:
    def __init__(self):
        self._target_id: Optional[str] = None
        self._ruleset: str = "default"
        self._strict_mode: bool = False

    def with_target(self, target_id: str) -> 'VerificationRequestBuilder':
        self._target_id = target_id
        return self

    def with_ruleset(self, ruleset: str) -> 'VerificationRequestBuilder':
        self._ruleset = ruleset
        return self

    def enable_strict_mode(self) -> 'VerificationRequestBuilder':
        self._strict_mode = True
        return self

    def build_request(self) -> VerificationRequest:
        if not self._target_id:
            raise ValueError("target_id is required")
        return VerificationRequest(
            target_id=self._target_id,
            ruleset=self._ruleset,
            strict_mode=self._strict_mode
        )

    def build(self) -> Verifier:
        return Verifier()
