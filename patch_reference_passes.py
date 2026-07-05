with open("omlx/optimization/reference_passes.py", "r") as f:
    content = f.read()

content = content.replace("from .passes import AnalysisPass, OptimizationPass, PassCategory, CompilerStage, OptimizationContext", "from .passes import AnalysisPass, OptimizationPass, PassCategory, CompilerStage, OptimizationContext, AnalysisResult\nfrom dataclasses import dataclass")

content = content.replace("class DependencyAnalysisPass(AnalysisPass):", """@dataclass(frozen=True)
class DependencyAnalysisResult(AnalysisResult):
    pass

class DependencyAnalysisPass(AnalysisPass):""")

content = content.replace("    def analyze(self, artifact: Any, context: OptimizationContext) -> None:", "    def analyze(self, artifact: Any, context: OptimizationContext) -> AnalysisResult:")
content = content.replace("""        if context.tracker:
            context.tracker.add_diagnostic(
                DiagnosticLevel.INFO,
                "Dependency analysis complete (reference implementation).",
                pass_name=self.name
            )""", """        if context.tracker:
            context.tracker.add_diagnostic(
                DiagnosticLevel.INFO,
                "Dependency analysis complete (reference implementation).",
                pass_name=self.name
            )
        return DependencyAnalysisResult()""")


content = content.replace("class MemoryAnalysisPass(AnalysisPass):", """@dataclass(frozen=True)
class MemoryAnalysisResult(AnalysisResult):
    pass

class MemoryAnalysisPass(AnalysisPass):""")

content = content.replace("    def analyze(self, artifact: Any, context: OptimizationContext) -> None:", "    def analyze(self, artifact: Any, context: OptimizationContext) -> AnalysisResult:")
content = content.replace("""        if context.tracker:
            context.tracker.add_diagnostic(
                DiagnosticLevel.INFO,
                "Memory analysis complete (reference implementation).",
                pass_name=self.name
            )""", """        if context.tracker:
            context.tracker.add_diagnostic(
                DiagnosticLevel.INFO,
                "Memory analysis complete (reference implementation).",
                pass_name=self.name
            )
        return MemoryAnalysisResult()""")

with open("omlx/optimization/reference_passes.py", "w") as f:
    f.write(content)
