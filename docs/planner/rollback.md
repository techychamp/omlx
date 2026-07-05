# Rollback Procedure

Because the Execution Planner is a newly introduced, passive layer, rolling back does not break existing inference paths.

1. **Revert Composition Root**: Remove `self.execution_planner = ExecutionPlanner()` from `omlx/runtime/builder.py`.
2. **Remove Module**: Delete the `omlx/planner` directory.
3. **Remove Tests**: Delete `tests/planner/test_planner.py`.
4. **Remove Docs**: Delete `docs/planner/`.

Existing code currently uses `ExecutionProfileRegistry` and will not be impacted by the removal of the planner.
