with open('omlx/planner/compiler/backend/adapter.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "def supports_capability(self, capability: str | BackendCapability) -> bool:" in line:
        # found it, skip the next line (pass)
        pass_idx = lines.index(line) + 1
        if "pass" in lines[pass_idx]:
             # wait, better way
             pass

import re
with open('omlx/planner/compiler/backend/adapter.py', 'r') as f:
    content = f.read()

base_execute = """
    @abc.abstractmethod
    def execute(self, operation: 'BackendOperation', context: Any) -> Any:
        \"\"\"Execute a single backend operation.\"\"\"
        pass
"""

# Just append it to BaseBackendAdapter before class MLXAdapter
content = content.replace("class MLXAdapter(BaseBackendAdapter):", base_execute + "\nclass MLXAdapter(BaseBackendAdapter):")

with open('omlx/planner/compiler/backend/adapter.py', 'w') as f:
    f.write(content)
