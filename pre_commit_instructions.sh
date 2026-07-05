echo "Doing pre commit verification"
PYTHONPATH=. /home/jules/.local/share/pipx/venvs/pytest/bin/python -m pytest -m "not slow" tests/plugins/
