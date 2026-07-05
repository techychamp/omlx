with open("tests/test_optimization.py", "r") as f:
    content = f.read()

content = content.replace("from omlx.optimization.passes import (", "from omlx.optimization.passes import (\n    AnalysisResult,")

with open("tests/test_optimization.py", "w") as f:
    f.write(content)
