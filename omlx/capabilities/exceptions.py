class CapabilityError(Exception):
    """Base exception for capability resolution errors."""
    pass

class CapabilityValidationError(CapabilityError):
    """Raised when capabilities fail logic validation."""
    pass

class CapabilityConflictError(CapabilityError):
    """Raised when conflicting capability sources cannot be resolved."""
    pass
