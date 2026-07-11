# Recommendations for BRIDGE-001

- Use the global `StreamingController` to push `StreamingEvent`s natively from the backend adapters.
- Maintain immutability of `StreamingToken`s during MLX/C++ to Python conversion.
- Inject early latency timing metrics when backend logic allows explicit measurements.
