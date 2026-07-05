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
    r'    @abc.abstractmethod\n    def supports_capability\(self, capability: str \| BackendCapability\) -> bool:\n        pass\n',
    r'    @abc.abstractmethod\n    def supports_capability(self, capability: str | BackendCapability) -> bool:\n        pass\n' + base_adapter_execute,
    content
)

# Add execute() to MLXAdapter
mlx_adapter_execute = """
    def execute(self, operation: BackendOperation, context: Any) -> Any:
        \"\"\"Execute a single MLX backend operation. Currently a pass-through mock.\"\"\"
        # This will be replaced with real MLX kernel invocation logic in BACKEND-005.
        return {"status": "executed", "operation_id": operation.id, "backend": "mlx"}
"""

content = re.sub(
    r'    def translate\(self, physical_ir: PhysicalIR\) -> TranslationResult:.*?return TranslationResult\(.*?\n        \)\n',
    lambda m: m.group(0) + mlx_adapter_execute,
    content,
    flags=re.DOTALL
)

with open('omlx/planner/compiler/backend/adapter.py', 'w') as f:
    f.write(content)
