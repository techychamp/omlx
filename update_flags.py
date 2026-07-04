import re

with open("omlx/runtime/feature_flags.py", "r") as f:
    content = f.read()

# Add new feature flags
new_flags = """    EXECUTION_PLAN_RUNTIME_ENABLED: bool = False
    EXECUTION_PROFILE_COMPATIBILITY_ENABLED: bool = False
    EXECUTION_PLAN_VALIDATION_ENABLED: bool = False
"""

# Add environment variable mapping
env_flags = """            EXECUTION_PLAN_RUNTIME_ENABLED=os.getenv("OMLX_FEATURE_EXECUTION_PLAN_RUNTIME", "0") == "1",
            EXECUTION_PROFILE_COMPATIBILITY_ENABLED=os.getenv("OMLX_FEATURE_EXECUTION_PROFILE_COMPATIBILITY", "0") == "1",
            EXECUTION_PLAN_VALIDATION_ENABLED=os.getenv("OMLX_FEATURE_EXECUTION_PLAN_VALIDATION", "0") == "1",
"""

content = re.sub(r'(    ADAPTER_RUNTIME_ENABLED: bool = False)', r'\1\n' + new_flags, content)
content = re.sub(r'(            ADAPTER_RUNTIME_ENABLED=os.getenv\("OMLX_FEATURE_ADAPTER_RUNTIME", "0"\) == "1",)', r'\1\n' + env_flags, content)

with open("omlx/runtime/feature_flags.py", "w") as f:
    f.write(content)
