with open("omlx/optimization/pipeline.py", "r") as f:
    content = f.read()

content = content.replace("        ordered_passes = self.manager.get_execution_order()", "        ordered_passes = self.manager.get_execution_order(stage=self.stage)")

content = content.replace("""        for p in ordered_passes:
            if self.stage not in p.supported_stages:
                if context.tracker:
                     context.tracker.add_diagnostic(
                         DiagnosticLevel.INFO,
                         f"Skipped pass '{p.name}' because it does not support stage {self.stage.name}.",
                         pass_name=p.name
                     )
                continue""", """        for p in ordered_passes:""")

with open("omlx/optimization/pipeline.py", "w") as f:
    f.write(content)
