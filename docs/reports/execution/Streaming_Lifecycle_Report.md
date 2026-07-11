# Streaming Lifecycle Report

1. **Initialization**: Client requests a streaming execution.
2. **Session Creation**: `StreamingController` creates a `StreamSession`.
3. **Event Observation**:
   - `SessionStarted` emitted.
   - During execution, `TokenGenerated`, `ExecutionProgress`, `StatisticsUpdated` are emitted by backend adapters.
4. **Token Emission**: `TokenEmitter` provides a consumer-friendly API to iterate over `StreamingToken`s.
5. **Completion / Cancellation**:
   - On success, `Completed` event is emitted.
   - On error, `Failed` event is emitted.
   - If client cancels, `Cancelled` event is emitted, and `StreamSession` is marked cancelled.
6. **Cleanup**: Resources are released gracefully.
