# Rollback Procedure

If this branch causes pipeline failures:
1. Revert the commit.
2. Since no runtime files were modified, a strict `git rm -rf omlx/compiler_perf tests/test_compiler_perf.py` guarantees absolute zero impact on the existing system.
