# Streaming Events Reference

Events emitted by the `StreamingController` are modeled through `StreamingEvent` and categorized by `StreamingEventType`.

- `SESSION_STARTED`: Emitted immediately upon session creation.
- `TOKEN_GENERATED`: Carries a `StreamingToken` as payload.
- `PARTIAL_RESPONSE_UPDATED`: Used when text chunks are delivered instead of individual tokens.
- `EXECUTION_PROGRESS`: Notifies intermediate progress before final completion.
- `STATISTICS_UPDATED`: Triggers statistic refresh actions.
- `WARNING`: Dispatches a non-fatal anomaly message.
- `COMPLETED`: Successful streaming termination.
- `CANCELLED`: Interruption by client.
- `FAILED`: Fatal exception occurred during generation.
