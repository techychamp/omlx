import re

with open('omlx/runtime/builder.py', 'r') as f:
    content = f.read()

# Replace execute_request
new_execute = """    def execute_request(self, request_context: Any) -> Any:
        \"\"\"
        Execute an incoming request using the Compiler service and Execution Engine.
        \"\"\"
        # Explicit legacy handling
        if self.feature_flags.LEGACY_RUNTIME_ENABLED and not self.feature_flags.COMPILER_RUNTIME_ENABLED:
            logger.debug("Falling back to legacy runtime execution.")
            # We don't have a legacy implementation in this file yet, so we raise NotImplementedError
            raise NotImplementedError("Legacy runtime execution is not yet implemented.")

        if self.feature_flags.COMPILER_RUNTIME_ENABLED:
            model_id = request_context.model

            # Use compiler to get graph directly instead of TranslationResult
            translation_result = self.compiler_service.run_compilation(model_id, request_context)
            if translation_result:
                logger.debug(f"Compiler pipeline successfully planned intent for {model_id}")

                # Execution Engine
                # We extract graph here, but future versions of CompilerService will return it directly
                backend_op_graph = getattr(translation_result, "backend_graph", getattr(translation_result, "backend_operation_graph", None))

                # Determine backend adapter
                adapter = None
                backend = getattr(translation_result, "backend_descriptor", None)
                if backend and hasattr(backend, "backend_id"):
                     adapter = self.adapter_registry.resolve(backend=backend.backend_id, hardware="any", execution_family="autoregressive", execution_mode="standard")
                elif self.adapter_registry:
                     adapter = self.adapter_registry.resolve(backend="mlx", hardware="any", execution_family="autoregressive", execution_mode="standard")

                # Construct ExecutionContext
                exec_context = ExecutionContext(
                    request_context=request_context,
                    backend_operation_graph=backend_op_graph,
                    diagnostics=getattr(translation_result, "diagnostics", None),
                    statistics=getattr(translation_result, "statistics", None),
                    adapter=adapter
                )

                execution_result = self.execution_engine.execute(exec_context)
                logger.debug(f"Execution Engine completed with status {execution_result.status}")

                return execution_result

        raise NotImplementedError("No execution path available for request.")"""

content = re.sub(r'    def execute_request\(self, request_context: Any\) -> Any:.*?return None', new_execute, content, flags=re.DOTALL)

with open('omlx/runtime/builder.py', 'w') as f:
    f.write(content)
