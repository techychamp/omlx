# SPDX-License-Identifier: Apache-2.0
"""Pipeline runner script executing stages and generating logs."""

import subprocess
import sys
import json
import os

class PipelineRunner:
    def __init__(self, model_id):
        self.model_id = model_id
        self.report = {"stages": {}}

    def run_stage(self, name, command):
        print(f"Executing Stage: {name} ...")
        res = subprocess.run(command, shell=True, capture_output=True, text=True)
        success = res.returncode == 0
        self.report["stages"][name] = {
            "success": success,
            "exit_code": res.returncode,
            "stdout": res.stdout[-500:],
            "stderr": res.stderr[-500:]
        }
        if not success:
            print(f"Stage {name} FAILED with exit code {res.returncode}")
            print(res.stderr)
            return False
        print(f"Stage {name} PASSED.")
        return True

    def execute_all(self):
        py_exe = sys.executable
        # 1. Golden validation
        if not self.run_stage("golden_assets", f"{py_exe} -m pytest verification/scripts/test_golden_assets.py"):
            return False

        # 2. Equivalence assertions
        if not self.run_stage("equivalence_assertions", f"{py_exe} -m pytest verification/scripts/test_equivalence_runner.py"):
            return False

        # 3. Capability profiles check
        if not self.run_stage("capability_profiles", f"{py_exe} -m pytest verification/scripts/test_capability_profiles.py"):
            return False

        # 4. Performance assertions check
        if not self.run_stage("performance_assertions", f"{py_exe} -m pytest verification/scripts/test_performance_assertions.py"):
            return False

        print("\nAll pipeline execution stages completed successfully.")
        return True

if __name__ == "__main__":
    runner = PipelineRunner("mock-llama-8b")
    success = runner.execute_all()
    sys.exit(0 if success else 1)
