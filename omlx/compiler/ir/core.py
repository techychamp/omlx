from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class Node:
    id: str
    type: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        return cls(**data)

@dataclass
class Edge:
    source_node: str
    target_node: str
    tensor_name: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Edge':
        return cls(**data)
