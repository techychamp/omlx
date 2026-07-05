class OmlxError(Exception):
    pass

class CompilerError(OmlxError):
    pass

class PlanningError(OmlxError):
    pass

class BackendError(OmlxError):
    pass

class VerificationError(OmlxError):
    pass

class PluginError(OmlxError):
    pass

class ConfigurationError(OmlxError):
    pass

class ValidationError(OmlxError):
    pass

class DiagnosticsError(OmlxError):
    pass
