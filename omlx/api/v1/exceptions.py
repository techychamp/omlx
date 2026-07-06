from typing import Any, Dict, Optional

class OmlxError(Exception):
    def __init__(
        self,
        message: str,
        category: str = "general",
        code: str = "ERROR",
        details: Optional[Dict[str, Any]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        recommendation: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.code = code
        self.details = details or {}
        self.diagnostics = diagnostics or {}
        self.recommendation = recommendation

class CompilerError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="compiler", **kwargs)

class PlanningError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="planning", **kwargs)

class BackendError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="backend", **kwargs)

class VerificationError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="verification", **kwargs)

class PluginError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="plugin", **kwargs)

class ConfigurationError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="configuration", **kwargs)

class ValidationError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="validation", **kwargs)

class DiagnosticsError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="diagnostics", **kwargs)

class OMLXRuntimeError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="runtime", **kwargs)

class StreamingError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="streaming", **kwargs)

class ModelError(OmlxError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category="model", **kwargs)
