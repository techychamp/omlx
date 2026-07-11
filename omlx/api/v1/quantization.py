# SPDX-License-Identifier: Apache-2.0
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QuantizationInfo(BaseModel):
    method: str
    bits: int
    group_size: int
    packing: Optional[str] = None
    recommended_hardware: Optional[List[str]] = None
    performance_class: Optional[str] = None

class QuantizationService:
    def get_info(self, model_id: str) -> QuantizationInfo:
        return QuantizationInfo(
            method="awq",
            bits=4,
            group_size=128,
            packing="awq_packed",
            recommended_hardware=["DISCRETE_GPU"],
            performance_class="HIGH"
        )
