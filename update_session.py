import re

file_path = "omlx/runtime/session.py"
with open(file_path, "r") as f:
    content = f.read()

batch_fields = """
    # Speculative Execution additions
    speculative_context: Optional[Any] = None
    verification_context: Optional[Any] = None
    speculative_statistics: Optional[Any] = None
    speculative_reports: List[Any] = field(default_factory=list)

    # Batch Realization additions
    batch_execution_graph: Optional[Any] = None
    batch_realization_report: Optional[Any] = None
"""

content = content.replace("""
    # Speculative Execution additions
    speculative_context: Optional[Any] = None
    verification_context: Optional[Any] = None
    speculative_statistics: Optional[Any] = None
    speculative_reports: List[Any] = field(default_factory=list)
""", batch_fields)

with open(file_path, "w") as f:
    f.write(content)
