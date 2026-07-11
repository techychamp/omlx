# IMP-004: Runtime Event Bus & Event System Walkthrough

## Architecture

The Runtime Event Bus introduces a loosely-coupled communication backbone for OMLX inference runtime components. It replaces direct dependencies and function calls between disparate systems like plugins, verification frameworks, metrics collection, and the core runtime execution pipeline.

### Key Components

1.  **Event Classes (`omlx.runtime.events`)**:
    *   `Event`: A strongly-typed object (maintaining legacy initialization compatibility) representing a single event. It contains metadata (`event_id`, `timestamp`, `source`, `correlation_id`, `request_id`, etc.) and a `payload`.
    *   `EventCategory`: Defines high-level categories of events (e.g., `RUNTIME`, `LIFECYCLE`, `EXECUTION`, `METRICS`).
    *   `LifecycleEvent`, `ExecutionEvent`, `RuntimeLifecycleEvent`: Enums defining specific event types.
    *   `EventContext`: Provides the environment the event operates in (tracing, cancellation tokens).

2.  **EventBus (`omlx.runtime.events.EventBus`)**:
    *   **Pub/Sub Model**: Centralized location for publishing events and subscribing handlers.
    *   **Priorities**: Handlers can be registered with a priority. Higher priority handlers execute first.
    *   **Filtering**: Handlers can provide a `filter_fn` to only receive events matching specific criteria (e.g., specific payload values).
    *   **Wildcards**: Handlers can subscribe to `*` to receive all events flowing through the bus.
    *   **Dispatch Modes**: Supports both `publish()` (synchronous) and `publish_async()` (asynchronous).
    *   **Error Isolation**: If an event handler raises an exception, the exception is caught (preventing the publisher/runtime from crashing), logged, and recorded in metrics. Other handlers continue to process the event.
    *   **Thread Safety**: Uses `threading.RLock()` to ensure subscriptions can be mutated safely in concurrent environments without deadlocks during publishing.
    *   **Metrics**: Internal tracking of published events, dispatched events, handler errors, and dispatch times.

3.  **RuntimeBuilder Integration (`omlx.runtime.builder`)**:
    *   The `Runtime` object now owns a single instance of `EventBus`.
    *   The `EventBus` is injected into components rather than existing as a global singleton.
    *   During initialization, `RuntimeBuilder` publishes `RuntimeLifecycleEvent.RUNTIME_STARTING` to signal the beginning of the boot process.

## Event Flow

1.  **Subscription**: A component (e.g., a metrics plugin) registers a handler during its initialization using `bus.subscribe("my_event", my_handler, priority=10)`.
2.  **Publishing**: The core execution engine reaches a specific state and publishes an event using `bus.publish(Event(type="my_event", payload={...}))`.
3.  **Dispatch**:
    *   The `EventBus` locks its subscriber list and resolves the handlers for `"my_event"`.
    *   It combines typed subscribers with wildcard (`*`) subscribers.
    *   It filters out any subscribers whose `filter_fn` evaluates to `False`.
    *   It sorts the combined list by priority (descending).
    *   It executes the handler callbacks sequentially outside of the lock to prevent deadlocks.
    *   If a handler fails, it logs the error, bumps the `handler_errors` metric, and continues to the next handler.

## Lifecycle Integration

The `EventBus` is initialized within `RuntimeBuilder` as a core part of the `Runtime` object. It does not exist as a global singleton. The `RuntimeBuilder.build()` method publishes the first lifecycle event (`RUNTIME_STARTING`), allowing plugins or other components to hook into the boot process immediately.

## Testing Evidence

Comprehensive tests have been written in `tests/test_runtime_event_bus.py` and `tests/test_runtime_builder.py`.
Tests cover:
*   **Basic Pub/Sub**: Verify handlers receive the correct events.
*   **Unsubscribe**: Verify handlers are successfully removed.
*   **Async Dispatch**: Verify events can be processed in a separate thread.
*   **Priority Ordering**: Verify high-priority handlers execute before low-priority ones.
*   **Error Isolation**: Verify a failing handler does not crash the system or prevent other handlers from executing.
*   **Wildcard Subscriptions**: Verify `*` subscriptions receive all events.
*   **Filtered Subscriptions**: Verify `filter_fn` properly excludes non-matching events.
*   **Thread Safety**: Verify concurrent subscribes, publishes, and unsubscribes do not crash or deadlock.
*   **Metrics**: Verify internal counters increment correctly.
*   **Runtime Integration**: Verify the builder correctly instantiates the bus and publishes the starting event without breaking existing dependency ownership tests.

## Migration Strategy

Currently, this checkpoint *only* introduces the infrastructure. Existing components that use direct coupling (e.g., directly calling a metrics function from the execution engine) have not been altered, respecting the strict requirement: "No inference behavior changes. No Scheduler modifications. No Engine modifications."

Future migrations should follow this pattern:
1.  Identify a tightly coupled call (e.g., Engine calling `metrics.record_token()`).
2.  Update the Engine to instead call `event_bus.publish(Event(type=ExecutionEvent.AFTER_EMIT, ...))`.
3.  Update the Metrics component to subscribe to `ExecutionEvent.AFTER_EMIT` during initialization and record the token there.
4.  Remove the direct reference to the Metrics component from the Engine.

## Future Extension Points

*   **Remote/Distributed Dispatch**: The `EventBus` could be extended to serialize events and publish them to an external message queue (like Redis, Kafka, or RabbitMQ) for distributed inference nodes.
*   **True Async Loop**: `publish_async()` currently spins up a simple `threading.Thread`. In an `asyncio`-heavy environment, this could be upgraded to push to an `asyncio.Queue` processed by an event loop.
*   **Tracing Context Integration**: The `EventContext` includes a `tracing_context` which can be populated with OpenTelemetry spans in the future to track events across distributed services.
