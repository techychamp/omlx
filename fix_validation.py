with open("omlx/optimization/validation.py", "r") as f:
    content = f.read()

content = content.replace("from typing import List, Dict, Set", "from typing import List, Dict, Set, Any")

with open("omlx/optimization/validation.py", "w") as f:
    f.write(content)
