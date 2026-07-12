from dataclasses import dataclass
from typing import Dict, Any, List
from omlx.compiler.operators.base import Operator

@dataclass
class Embedding(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class Attention(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class Linear(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class RMSNorm(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class LayerNorm(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class MLP(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class MoE(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class Conv(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class VisionEncoder(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class AudioEncoder(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class Projection(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class Sampling(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class Tokenizer(Operator):
    def memory_estimate(self) -> int:
        return 0

@dataclass
class KVCache(Operator):
    def memory_estimate(self) -> int:
        return 0
