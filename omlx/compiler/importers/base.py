from abc import ABC, abstractmethod
from omlx.compiler.artifacts import CompilerArtifact
from omlx.compiler.cmr.models import CanonicalModelRepresentation
from omlx.compiler.graph.builder import Graph

class BaseImporter(ABC):
    @abstractmethod
    def build_cmr(self, model_path: str, artifact: CompilerArtifact = None) -> CanonicalModelRepresentation:
        pass

    @abstractmethod
    def generate_ir(self, model_path: str, cmr: CanonicalModelRepresentation) -> Graph:
        pass
