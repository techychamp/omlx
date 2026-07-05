with open("omlx/optimization/passes.py", "r") as f:
    content = f.read()

analysis_result_class = """
class AnalysisResult(ABC):
    \"\"\"Base class for reusable, immutable analysis results.\"\"\"
    pass

class BasePass(ABC):
"""

content = content.replace("class BasePass(ABC):", analysis_result_class)

content = content.replace("    def __init__(self, tracker: Any = None, stats: Any = None):", "    def __init__(self, tracker: Any = None, stats: Any = None, analysis_cache: Any = None):")
content = content.replace("        self.stats = stats", "        self.stats = stats\n        self.analysis_cache = analysis_cache if analysis_cache is not None else {}")

content = content.replace("    @abstractmethod\n    def analyze(self, artifact: T, context: OptimizationContext) -> None:", "    @abstractmethod\n    def analyze(self, artifact: T, context: OptimizationContext) -> AnalysisResult:")

content = content.replace("""    def apply(self, artifact: T, context: OptimizationContext) -> T:
        \"\"\"Applies analysis. Returns the artifact unmodified.\"\"\"
        self.analyze(artifact, context)
        return artifact""", """    def apply(self, artifact: T, context: OptimizationContext) -> T:
        \"\"\"Applies analysis and caches the result. Returns the artifact unmodified.\"\"\"
        # Generate cache key based on artifact identity/version if possible. For simplicity, just use pass name.
        cache_key = self.name
        if context.analysis_cache is not None and cache_key in context.analysis_cache:
            if context.tracker:
                 from .diagnostics import DiagnosticLevel
                 context.tracker.add_diagnostic(
                     DiagnosticLevel.INFO,
                     f"Analysis reused for pass '{self.name}'.",
                     pass_name=self.name
                 )
            return artifact

        result = self.analyze(artifact, context)

        if result is not None and context.analysis_cache is not None:
            context.analysis_cache[cache_key] = result

        return artifact""")

with open("omlx/optimization/passes.py", "w") as f:
    f.write(content)
