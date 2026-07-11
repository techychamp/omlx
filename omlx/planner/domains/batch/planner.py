from typing import List, Optional
from omlx.planner.domains.batch.artifacts import (
    BatchPlan,
    BatchDescriptor,
    BatchRequirement,
    BatchCompatibilityReport
)

class BatchPlanner:
    def plan(self, request_ids: List[str], max_batch_size: int = 32, max_tokens: int = 2048) -> BatchPlan:
        descriptor = BatchDescriptor(
            batch_id="batch_0",
            request_ids=list(request_ids)
        )
        requirements = BatchRequirement(
            max_batch_size=max_batch_size,
            max_tokens=max_tokens
        )
        compatibility_report = BatchCompatibilityReport(is_compatible=True)

        return BatchPlan(
            batch_descriptor=descriptor,
            requirements=requirements,
            compatibility_report=compatibility_report
        )
