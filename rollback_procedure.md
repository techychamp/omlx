# Rollback Procedure

## In case of regression

1. **Immediate Action:**
   Revert the commit that merged BACKEND-003.

2. **Code Impact:**
   The only modified repository file outside of adding new structures is `omlx/planner/compiler/backend/registry.py`. A simple `git revert` or checkout of the previous state of this file will restore the old behavior (which only appended a single item to a dictionary).

3. **No Database/State Impact:**
   Because all these changes are strictly architectural metadata loaded at boot, no persistent state or external resources require migration or teardown.
