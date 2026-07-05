with open("omlx/optimization/statistics.py", "r") as f:
    content = f.read()

content = content.replace("""    def __init__(self):
        self._executions: List[PassExecutionStats] = []
        self._total_duration_ms: float = 0.0""", """    def __init__(self):
        self._executions: List[PassExecutionStats] = []
        self._total_duration_ms: float = 0.0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.parallel_executions: int = 0""")

content = content.replace("""    def get_summary(self) -> Dict[str, Any]:
        successful_passes = sum(1 for e in self._executions if e.success)
        failed_passes = len(self._executions) - successful_passes
        total_nodes_removed = sum(e.nodes_removed for e in self._executions)

        return {
            "total_passes_run": len(self._executions),
            "successful_passes": successful_passes,
            "failed_passes": failed_passes,
            "total_execution_time_ms": self._total_duration_ms,
            "total_nodes_removed": total_nodes_removed,
        }""", """    def get_summary(self) -> Dict[str, Any]:
        successful_passes = sum(1 for e in self._executions if e.success)
        failed_passes = len(self._executions) - successful_passes
        total_nodes_removed = sum(e.nodes_removed for e in self._executions)

        cache_hit_rate = 0.0
        total_cache = self.cache_hits + self.cache_misses
        if total_cache > 0:
            cache_hit_rate = self.cache_hits / total_cache

        return {
            "total_passes_run": len(self._executions),
            "successful_passes": successful_passes,
            "failed_passes": failed_passes,
            "total_execution_time_ms": self._total_duration_ms,
            "total_nodes_removed": total_nodes_removed,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "parallel_executions": self.parallel_executions
        }""")

content = content.replace("""class StatisticsCollector:""", """class StatisticsCollector:
    def record_cache_hit(self): self.cache_hits += 1
    def record_cache_miss(self): self.cache_misses += 1
    def record_parallel_execution(self): self.parallel_executions += 1
""")

with open("omlx/optimization/statistics.py", "w") as f:
    f.write(content)


with open("omlx/optimization/passes.py", "r") as f:
    content = f.read()

content = content.replace("""            if context.tracker:
                 from .diagnostics import DiagnosticLevel
                 context.tracker.add_diagnostic(
                     DiagnosticLevel.INFO,
                     f"Analysis reused for pass '{self.name}'.",
                     pass_name=self.name
                 )
            return artifact""", """            if context.tracker:
                 from .diagnostics import DiagnosticLevel
                 context.tracker.add_diagnostic(
                     DiagnosticLevel.INFO,
                     f"Analysis reused for pass '{self.name}'.",
                     pass_name=self.name
                 )
            if context.stats:
                 context.stats.record_cache_hit()
            return artifact""")

content = content.replace("""        if result is not None and context.analysis_cache is not None:
            context.analysis_cache[cache_key] = result""", """        if result is not None and context.analysis_cache is not None:
            context.analysis_cache[cache_key] = result
        if context.stats:
            context.stats.record_cache_miss()""")

with open("omlx/optimization/passes.py", "w") as f:
    f.write(content)


with open("omlx/optimization/pipeline.py", "r") as f:
    content = f.read()

content = content.replace("""                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = [executor.submit(execute_pass, gp, current_artifact, context) for gp in analysis_group]
                        for future in concurrent.futures.as_completed(futures):
                            # Artifact shouldn't change for analysis passes
                            future.result()
                    idx = next_idx
                    continue""", """                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        futures = [executor.submit(execute_pass, gp, current_artifact, context) for gp in analysis_group]
                        for future in concurrent.futures.as_completed(futures):
                            # Artifact shouldn't change for analysis passes
                            future.result()
                    if context.stats:
                        context.stats.record_parallel_execution()
                    idx = next_idx
                    continue""")

with open("omlx/optimization/pipeline.py", "w") as f:
    f.write(content)
