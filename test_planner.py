import pytest
import sys
import os

print(os.getcwd())
sys.path.insert(0, os.getcwd())

# let's run pytest tests -k planner
