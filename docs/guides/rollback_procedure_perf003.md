# Rollback Procedure

Since no existing runtime or compiler behavior was altered, rolling back PERF-003 simply requires removing the `omlx/optimization` module and `tests/test_optimization.py`.
