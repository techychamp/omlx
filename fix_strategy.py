import re

with open("omlx/runtime/generation/strategy.py", "r") as f:
    content = f.read()

replacement = """
    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:
        \"\"\"
        Orchestrates generation according to the specific strategy.
        \"\"\"
        ...

    def get_cache_policy(self) -> dict:
        \"\"\"
        Returns the cache usage policy for this strategy.
        \"\"\"
        return {"use_cache": True, "policy": "standard"}
"""

content = content.replace("""
    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:
        \"\"\"
        Orchestrates generation according to the specific strategy.
        \"\"\"
        ...""", replacement)

with open("omlx/runtime/generation/strategy.py", "w") as f:
    f.write(content)

with open("omlx/runtime/generation/standard.py", "r") as f:
    content = f.read()

if "get_cache_policy" not in content:
    content = content.replace(
        "    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:",
        "    def get_cache_policy(self) -> dict:\n        return {\"use_cache\": True, \"policy\": \"standard\"}\n\n    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:"
    )

with open("omlx/runtime/generation/standard.py", "w") as f:
    f.write(content)

with open("omlx/runtime/generation/speculative.py", "r") as f:
    content = f.read()

if "get_cache_policy" not in content:
    content = content.replace(
        "    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:",
        "    def get_cache_policy(self) -> dict:\n        return {\"use_cache\": True, \"policy\": \"speculative\"}\n\n    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:"
    )

with open("omlx/runtime/generation/speculative.py", "w") as f:
    f.write(content)
