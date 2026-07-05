import re

# Update graph_executor to not mutate context
with open('omlx/runtime/execution/graph_executor.py', 'r') as f:
    content = f.read()

content = content.replace("setattr(context, '_execution_order', execution_order)", "# setattr removed")
content = content.replace("dispatch_result = self.dispatcher.dispatch(graph, context)", "dispatch_result = self.dispatcher.dispatch(graph, context, execution_order=execution_order)")

with open('omlx/runtime/execution/graph_executor.py', 'w') as f:
    f.write(content)

# Update dispatcher to accept execution_order
with open('omlx/runtime/execution/dispatcher.py', 'r') as f:
    content = f.read()

content = content.replace("def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:", "def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext, execution_order=None) -> ExecutionResult:")
content = content.replace("execution_order = getattr(context, '_execution_order', None)", "")

with open('omlx/runtime/execution/dispatcher.py', 'w') as f:
    f.write(content)

# Update interfaces
with open('omlx/runtime/execution/interfaces.py', 'r') as f:
    content = f.read()

content = content.replace("def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:", "def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext, execution_order=None) -> ExecutionResult:")

with open('omlx/runtime/execution/interfaces.py', 'w') as f:
    f.write(content)

# Update context to include adapter
with open('omlx/runtime/execution/context.py', 'r') as f:
    content = f.read()

content = content.replace("statistics: Optional[Any] = None", "statistics: Optional[Any] = None\n    adapter: Optional[Any] = None")

with open('omlx/runtime/execution/context.py', 'w') as f:
    f.write(content)
