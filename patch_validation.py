with open("omlx/optimization/pipeline.py", "r") as f:
    content = f.read()

content = content.replace("from .validation import PassValidationError", "from .validation import PassValidationError, validate_artifact_immutability")

immutability_check = """
            # Execute single pass
            old_artifact = current_artifact
            current_artifact = execute_pass(p, current_artifact, context)

            # Validate immutability
            validate_artifact_immutability(old_artifact, current_artifact, p)

            idx += 1"""

content = content.replace("""            # Execute single pass
            current_artifact = execute_pass(p, current_artifact, context)
            idx += 1""", immutability_check)

with open("omlx/optimization/pipeline.py", "w") as f:
    f.write(content)


with open("omlx/optimization/validation.py", "a") as f:
    f.write("""

def validate_artifact_immutability(old_artifact: Any, new_artifact: Any, pass_: BasePass) -> None:
    \"\"\"
    Validates that if a pass changed the logical content of the artifact,
    it returned a NEW object (or the artifact is immutable).
    This is a simplistic check: if it's the exact same object and a mutating
    pass claimed to have changed it (or an AnalysisPass returned it), we assume
    it's valid unless we can prove deep mutation. For now, we enforce that
    AnalysisPasses return the exact same object, and OptimizationPasses return
    either the same (no change) or a new object.
    \"\"\"
    from .passes import AnalysisPass
    if isinstance(pass_, AnalysisPass):
        if id(old_artifact) != id(new_artifact):
            raise PassValidationError(f"AnalysisPass '{pass_.name}' illegally returned a new artifact instance.")
    else:
        # For OptimizationPass, we can't easily detect in-place mutation without deep copies,
        # but we can hook into this function later for deeper checks if artifacts support it.
        pass
""")
