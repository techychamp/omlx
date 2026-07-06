import re

with open("omlx/runtime/compiler_integration.py", "r") as f:
    content = f.read()

# Make sure CompilerPipelineRunner class is correctly defined
if "class CompilerPipelineRunner:" not in content:
    print("WARNING: CompilerPipelineRunner class missing!")
    # Check if there is something else that looks like it
    print(content[:500])
