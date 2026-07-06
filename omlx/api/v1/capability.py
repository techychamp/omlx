from typing import List, Dict, Any
from pydantic import BaseModel, Field

class CapabilityInfo(BaseModel):
    name: str
    supported: bool
    version: str

class CapabilityService:
    def list_capabilities(self) -> List[CapabilityInfo]:
        return [CapabilityInfo(name="attention", supported=True, version="1.0")]
