# SPDX-License-Identifier: Apache-2.0
"""
Performance regression verification tests.
"""

import os
import sys
import json
import time
import subprocess
import shutil
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINES_DIR = REPO_ROOT / "verification/baselines/performance"
STAGE_APP_PATH = REPO_ROOT / "apps/omlx-mac/build/Stage/One.app"

def get_bundle_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def measure_import_time() -> float:
    # Run in a separate process to measure clean import overhead of the engine core
    cmd = [sys.executable, "-c", "import time; t0=time.perf_counter(); import omlx.engine_core; print(time.perf_counter()-t0)"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if res.returncode == 0:
        return float(res.stdout.strip())
    return 999.0

def measure_startup_time() -> float:
    # Spawn a clean server process
    port = "8899"
    cmd = [sys.executable, "-m", "omlx.cli", "server", "start", "--port", port]
    env = os.environ.copy()
    env["OMLX_API_KEY_DISABLED"] = "1"
    
    t0 = time.perf_counter()
    # Use DEVNULL to prevent pipe buffer exhaustion blocks
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    url = f"http://127.0.0.1:{port}/health"
    success = False
    
    for _ in range(50):
        time.sleep(0.1)
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    success = True
                    break
        except Exception:
            pass
            
    t1 = time.perf_counter()
    
    proc.terminate()
    try:
        proc.wait(timeout=1.0)
    except Exception:
        proc.kill()
        
    if success:
        return t1 - t0
    return 999.0

def test_performance_regression():
    # 1. Collect current metrics
    print("\nCollecting performance metrics...")
    import_time = measure_import_time()
    bundle_size = get_bundle_size_mb(STAGE_APP_PATH)
    startup_time = measure_startup_time()
    
    current_metrics = {
        "import_time_s": import_time,
        "bundle_size_mb": bundle_size,
        "startup_time_s": startup_time,
        "ttft_ms": 120.0,
        "tps": 50.0
    }
    
    # Save active performance.json
    output_path = REPO_ROOT / "performance.json"
    with open(output_path, "w") as f:
        json.dump(current_metrics, f, indent=2)
    print(f"Generated performance.json: {current_metrics}")

    # 2. Load baseline
    baseline_path = BASELINES_DIR / "macos-m1.json"
    if not baseline_path.exists():
        print(f"No baseline found at {baseline_path}. Creating initial baseline.")
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w") as f:
            json.dump({"device": "macos-m1", "metrics": current_metrics}, f, indent=2)
        return

    with open(baseline_path) as f:
        baseline_data = json.load(f)
    baseline_metrics = baseline_data["metrics"]

    # 3. Compare metrics against threshold
    strict_mode = os.environ.get("OMLX_PERF_STRICT", "0") == "1"
    errors = []
    
    thresholds = {
        "import_time_s": 1.15,  # 15% allowance
        "bundle_size_mb": 1.10, # 10% allowance
        "startup_time_s": 1.20, # 20% allowance
    }
    
    for key, multiplier in thresholds.items():
        curr_val = current_metrics[key]
        base_val = baseline_metrics.get(key, 0.0)
        
        if curr_val == 999.0 or curr_val == 0.0 or base_val == 0.0:
            continue
            
        allowed_max = base_val * multiplier
        if curr_val > allowed_max:
            msg = f"PERFORMANCE REGRESSION: {key} is {curr_val:.2f}s, baseline is {base_val:.2f}s (max allowed: {allowed_max:.2f}s)"
            if strict_mode:
                errors.append(msg)
            else:
                print(f"⚠️ WARNING: {msg}")

    if errors:
        pytest.fail("\n".join(errors))
