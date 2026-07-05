import re

with open('omlx/runtime/builder.py', 'r') as f:
    content = f.read()

# Add import for ExecutionEngine and Context
import_statement = "from omlx.runtime.execution import ExecutionEngine, ExecutionContext\n"
content = re.sub(r'from typing import Any, Optional\n', f'from typing import Any, Optional\n{import_statement}', content)

# Inject ExecutionEngine instantiation in Runtime.__init__
init_injection = """        self.adapter_registry = context.adapter_registry
        self.descriptor_registry = context.descriptor_registry
        self.execution_engine = ExecutionEngine()"""

content = content.replace(
    "        self.adapter_registry = context.adapter_registry\n        self.descriptor_registry = context.descriptor_registry",
    init_injection
)

# Rewrite execute_request
new_execute_request = """    def execute_request(self, request_context: Any) -> Any:
        \"\"\"
        Execute an incoming request using the Compiler service and Execution Engine.
        \"\"\"
        # Fallback to legacy behavior if feature flags say so
        if self.feature_flags.LEGACY_RUNTIME_ENABLED and not self.feature_flags.COMPILER_RUNTIME_ENABLED:
            logger.debug("Falling back to legacy runtime execution.")
            return None # Assuming legacy handling occurs elsewhere since this method only had compiler paths

        if self.feature_flags.COMPILER_RUNTIME_ENABLED:
            model_id = request_context.model
            translation_result = self.compiler_service.run_compilation(model_id, request_context)
            if translation_result:
                logger.debug(f"Compiler pipeline successfully planned intent for {model_id}")

                # Execution Engine
                backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None))

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None)
                )

                execution_result = self.execution_engine.execute(exec_context)
                logger.debug(f"Execution Engine completed with status {execution_result.status}")

                return execution_result

        return None"""

content = re.sub(
    r'    def execute_request\(self, request_context: Any\) -> Any:.*?return None',
    new_execute_request,
    content,
    flags=re.DOTALL
)

with open('omlx/runtime/builder.py', 'w') as f:
    f.write(content)

print("Updated omlx/runtime/builder.py")
