from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(frozen=True)
class DiffusionCompatibilityReport:
    """Report on compatibility of diffusion requirements."""
    is_compatible: bool
    incompatibilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DiffusionValidationReport:
    """Report on validation of diffusion plans."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
