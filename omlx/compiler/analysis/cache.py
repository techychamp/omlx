# SPDX-License-Identifier: Apache-2.0

import pickle
import json
from pathlib import Path
from typing import Optional
from .artifact import CapabilityReport, AnalysisFingerprint

class AnalysisCache:
    """Persists analysis artifacts for reuse."""

    def __init__(self, cache_dir: str = ".omlx_cache/analysis"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_bin_path(self, model_hash: str) -> Path:
        return self.cache_dir / f"{model_hash}.analysis.bin"

    def _get_json_path(self, model_hash: str) -> Path:
        return self.cache_dir / f"{model_hash}.analysis.json"

    def save(self, report: CapabilityReport) -> None:
        """Saves the report as both a binary artifact and JSON export."""
        model_hash = report.fingerprint.model_hash

        # Save Binary (for Planner) - Convert dict back to objects during load since mappingproxy is not picklable natively easily.
        # So we just dump the dict rep and load it back.
        with open(self._get_bin_path(model_hash), "wb") as f:
            pickle.dump(report.to_dict(), f)

        # Save JSON (for Export/Telemetry)
        with open(self._get_json_path(model_hash), "w") as f:
            f.write(report.to_json())

    def load(self, fingerprint: AnalysisFingerprint) -> Optional[CapabilityReport]:
        """Loads and validates the cached report using the fingerprint."""
        path = self._get_bin_path(fingerprint.model_hash)

        if not path.exists():
            return None

        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                report: CapabilityReport = CapabilityReport.from_dict(data)

            # Validate Fingerprint (Ignore timestamp)
            if (report.fingerprint.compiler_version == fingerprint.compiler_version and
                report.fingerprint.ir_version == fingerprint.ir_version and
                report.fingerprint.analysis_version == fingerprint.analysis_version):
                return report

        except Exception:
            pass # Invalid cache file

        return None
