import re

with open("omlx/plugins/registry.py", "r") as f:
    content = f.read()

content = content.replace("capability.value in desc.capabilities", "capability in desc.capabilities")

with open("omlx/plugins/registry.py", "w") as f:
    f.write(content)
