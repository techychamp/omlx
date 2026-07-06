# SPDX-License-Identifier: Apache-2.0
"""
Validation Helpers
Tools to validate configurations and compatibility without executing them.
"""
from typing import Any, Dict, List
from omlx.api.v1.runtime import RuntimeConfig

class ValidationReport:
    """Structured report of validation findings."""
    def __init__(self, errors: List[str], warnings: List[str]):
        self.errors = errors
        self.warnings = warnings
        self.is_valid = len(errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

class ValidationHelper:
    """Helper to validate various runtime and compiler objects."""

    def validate_runtime_config(self, config: RuntimeConfig) -> ValidationReport:
        """Validates a RuntimeConfig object."""
        errors = []
        warnings = []

        # Simple structural validation for now
        if not isinstance(config.settings, dict):
            errors.append("Settings must be a dictionary.")

        if not isinstance(config.feature_flags, dict):
             errors.append("Feature flags must be a dictionary.")

        return ValidationReport(errors, warnings)

    def validate_plugin_compatibility(self, plugin: Any, runtime_version: str) -> ValidationReport:
        """Validates if a plugin is compatible with the runtime."""
        # Stub implementation
        return ValidationReport([], [])
