# SPDX-License-Identifier: Apache-2.0
"""
Compatibility Analysis Logic.

Determines compatibility with subsystems without modifying them.
"""

from typing import Dict, Any

class CompatibilityAnalyzer:
    """
    Analyzes model compatibility with subsystems.
    """
    def analyze(self, descriptor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produces an immutable compatibility report based on extracted descriptor data.
        """
        family = descriptor_data.get("model_family", "")
        caps = descriptor_data.get("capabilities", {})

        report = {
            "runtime_compatible": True,
            "compiler_compatible": True,
            "backend_compatible": True,
            "quantization_compatible": caps.get("quantization_support", False),
            "streaming_compatible": caps.get("streaming_support", False),
            "plugins_compatible": True,
            "api_compatible": True,
            "tooling_compatible": True,
            "details": {}
        }

        # Simple heuristics for compatibility
        if family == "Unknown":
            report["runtime_compatible"] = False
            report["compiler_compatible"] = False
            report["backend_compatible"] = False
            report["details"]["reason"] = "Unknown architecture family."

        if family == "Speech-to-Text" and not caps.get("audio_support", False):
             report["backend_compatible"] = False
             report["details"]["audio"] = "Audio support missing for Speech-to-Text model."

        return report
