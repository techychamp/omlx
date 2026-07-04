# Rollback Procedure

To rollback BACKEND-001:
1. Revert `omlx/planner/compiler/backend/descriptor.py`, `adapter.py`, and `operations.py` to their state prior to the BACKEND-001 commit.
2. Remove `tests/test_backend_evolution.py`.
3. Delete the `docs/architecture/backend` directory.
