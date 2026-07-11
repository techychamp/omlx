# Recommendations for Performance Profiling

Performance profiling should ingest `statistics.json` and timeline traces exported by the Bundle to analyze compiler bottlenecks, without instrumenting backend-specific mutable operations.