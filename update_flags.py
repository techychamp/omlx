import re

with open("omlx/runtime/feature_flags.py", "r") as f:
    content = f.read()

# Add CACHE_PLANNING_ENABLED and CACHE_RUNTIME_ENABLED to FeatureFlags
if "CACHE_PLANNING_ENABLED" not in content:
    content = re.sub(
        r'(COMPILER_COMPATIBILITY_MODE: bool = False)',
        r'\1\n    CACHE_PLANNING_ENABLED: bool = False\n    CACHE_RUNTIME_ENABLED: bool = False',
        content
    )

    content = re.sub(
        r'(COMPILER_COMPATIBILITY_MODE=os\.getenv\("OMLX_FEATURE_COMPILER_COMPATIBILITY_MODE", "0"\) == "1",)',
        r'\1\n            CACHE_PLANNING_ENABLED=os.getenv("OMLX_FEATURE_CACHE_PLANNING", "0") == "1",\n            CACHE_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_CACHE_RUNTIME", "0") == "1",',
        content
    )

with open("omlx/runtime/feature_flags.py", "w") as f:
    f.write(content)
