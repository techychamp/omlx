import re

with open('omlx/planner/compiler/backend/adapter.py', 'r') as f:
    content = f.read()

# Add execute() to BaseBackendAdapter
base_adapter_execute = """
    @abc.abstractmethod
    def execute(self, operation: BackendOperation, context: Any) -> Any:
        \"\"\"Execute a single backend operation.\"\"\"
        pass
"""

content = re.sub(
    r'(    @abc.abstractmethod\n    def supports_capability\(self, capability: str \| BackendCapability\) -> bool:\n        pass)',
    r'\1\n' + base_adapter_execute,
    content
)

with open('omlx/planner/compiler/backend/adapter.py', 'w') as f:
    f.write(content)
