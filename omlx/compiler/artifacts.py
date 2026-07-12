from dataclasses import dataclass, field
import datetime
from typing import Optional

@dataclass
class CompilerArtifact:
    version: int = 1
    generator: str = "omlx.compiler"
    hash: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    compiler_version: str = "0.1.0"
