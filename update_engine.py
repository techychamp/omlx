import re

file_path = "omlx/planner/compiler/engine.py"
with open(file_path, "r") as f:
    content = f.read()

import_statement = "from omlx.planner.domains.diffusion.transformation.pass_ import DiffusionRealizationPass\nfrom omlx.planner.compiler.batch.transformation.pass_ import BatchRealizationPass\n"
content = content.replace("from omlx.planner.domains.diffusion.transformation.pass_ import DiffusionRealizationPass\n", import_statement)

injection = """            # Conditionally inject Batch realization pass if plan is provided
            if planning_bundle and getattr(planning_bundle, 'batch_plan', None):
                 batch_pass = BatchRealizationPass(planning_bundle.batch_plan)
                 logical_ir = batch_pass.apply(logical_ir)
                 if batch_pass.report:
                     get_observer().track_artifact("BatchTransformationReport", batch_pass.report)

            # 1. Logical Optimization"""

content = content.replace("            # 1. Logical Optimization", injection)

with open(file_path, "w") as f:
    f.write(content)
