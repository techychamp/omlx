from typing import List, Dict, Any
from pydantic import BaseModel, Field

class QuantizationInfo(BaseModel, frozen=True):
    method: str
    bits: int
    group_size: int

class QuantizationService:
    def get_info(self, model_id: str) -> QuantizationInfo:
        return QuantizationInfo(method="awq", bits=4, group_size=128)
