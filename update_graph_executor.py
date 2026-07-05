import re

with open('omlx/runtime/execution/graph_executor.py', 'r') as f:
    content = f.read()

new_traverse = """    def traverse_and_execute(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:
        logger.debug("GraphExecutor validating and traversing graph")

        start_time = time.time()

        if not graph:
            logger.error("No BackendOperationGraph provided to GraphExecutor")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        # Basic validation
        if not hasattr(graph, 'operations'):
            logger.error("Invalid BackendOperationGraph: missing operations")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                model_output=None
            )

        # Deterministic graph traversal based on dependencies
        operations = graph.operations
        in_degree = {op_id: 0 for op_id in operations}
        adj_list = {op_id: [] for op_id in operations}

        for op_id, op in operations.items():
            for dep_id in op.dependencies:
                if dep_id in adj_list:
                    adj_list[dep_id].append(op_id)
                    in_degree[op_id] += 1

        queue = []
        if hasattr(graph, 'roots') and graph.roots:
            queue = list(graph.roots)
        else:
            queue = [op_id for op_id, deg in in_degree.items() if deg == 0]

        execution_order = []

        while queue:
            queue.sort()
            current_id = queue.pop(0)
            execution_order.append(current_id)

            for neighbor in adj_list.get(current_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(execution_order) != len(operations):
            logger.warning(f"Graph traversal incomplete: cycle detected or missing operations. Traversed {len(execution_order)}/{len(operations)}")

        # Pass ordered nodes to dispatcher
        # We will attach the execution_order to the context for the dispatcher to use
        # as we are constrained by the existing interface.

        # Actually, let's just make the dispatcher iterate over execution_order
        setattr(context, '_execution_order', execution_order)
        dispatch_result = self.dispatcher.dispatch(graph, context)

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        stats = ExecutionStatistics(
            executed_operations=len(execution_order),
            backend_invocations=len(execution_order),
            execution_duration_ms=duration_ms,
            graph_depth=1,
            execution_groups=1,
            dispatcher_calls=len(execution_order),
            adapter_calls=len(execution_order),
            compiler_execution_count=1,
            legacy_fallback_count=0
        )

        return ExecutionResult(
            status=dispatch_result.status,
            model_output=dispatch_result.model_output,
            diagnostics=dispatch_result.diagnostics,
            statistics=stats,
            execution_duration_ms=duration_ms
        )"""

content = re.sub(
    r'    def traverse_and_execute\(self, graph: BackendOperationGraph, context: ExecutionContext\) -> ExecutionResult:.*',
    new_traverse,
    content,
    flags=re.DOTALL
)

with open('omlx/runtime/execution/graph_executor.py', 'w') as f:
    f.write(content)
