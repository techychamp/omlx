with open("omlx/optimization/pipeline.py", "r") as f:
    content = f.read()

content = content.replace("from .passes import CompilerStage, OptimizationContext", "from .passes import CompilerStage, OptimizationContext, PassCategory\nfrom .validation import PassValidationError")

pipeline_phases_logic = """        ordered_passes = self.manager.get_execution_order(stage=self.stage)

        # Validate Phase Ordering
        phase_order = {
            PassCategory.CANONICALIZATION: 1,
            PassCategory.ANALYSIS: 2,
            PassCategory.SIMPLIFICATION: 3,
            PassCategory.OPTIMIZATION: 4,
            PassCategory.VALIDATION: 5,
            PassCategory.BACKEND_PREPARATION: 6
        }

        current_phase_idx = 0
        for p in ordered_passes:
            if p.category in phase_order:
                pass_phase_idx = phase_order[p.category]
                if pass_phase_idx < current_phase_idx:
                    raise PassValidationError(f"Phase ordering violation: Pass '{p.name}' (Category: {p.category.name}) executed after a later phase.")
                current_phase_idx = pass_phase_idx

        for p in ordered_passes:"""

content = content.replace("""        ordered_passes = self.manager.get_execution_order(stage=self.stage)

        for p in ordered_passes:""", pipeline_phases_logic)

with open("omlx/optimization/pipeline.py", "w") as f:
    f.write(content)
