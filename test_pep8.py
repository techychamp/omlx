import py_compile
import sys

files = [
    "omlx/framework/cache/descriptor.py",
    "omlx/framework/cache/plan.py",
    "omlx/framework/cache/__init__.py",
    "omlx/planner/cache_planner.py",
    "omlx/runtime/execution/cache_session.py",
    "omlx/api/v1/cache.py",
]

for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"{f}: OK")
    except py_compile.PyCompileError as e:
        print(f"{f}: FAILED - {e}")
        sys.exit(1)
print("All files compiled successfully.")
