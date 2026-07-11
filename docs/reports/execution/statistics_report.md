# Optimization Statistics Report

The `StatisticsCollector` tracks pass execution metrics, such as:
- Total execution time
- Pass success/failure rates
- Number of nodes added/removed

These statistics are accumulated in the `OptimizationContext` and can be retrieved via `.get_summary()`.
