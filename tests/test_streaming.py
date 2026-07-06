# SPDX-License-Identifier: Apache-2.0

import pytest
import time
import threading

from omlx.runtime.streaming import (
    StreamingController,
    StreamingEventType,
    StreamingEvent,
    StreamingToken,
    StreamCompletion,
    TokenEmitter,
    get_controller
)

def test_stream_session_lifecycle():
    controller = StreamingController()
    session = controller.create_session()

    assert session is not None
    assert session.is_active is True

    controller.complete_session(session.session_id, StreamCompletion.SUCCESS)
    assert session.is_active is False

    stats = session.get_statistics()
    assert stats.tokens_emitted == 0
    assert stats.events_published > 0

def test_event_ordering_and_token_emission():
    controller = StreamingController()
    session = controller.create_session()

    emitter = TokenEmitter()
    emitter.set_context(session.session_id, controller)
    controller.subscribe(session.session_id, emitter)

    # Simulate background token generation
    def generator():
        for i in range(3):
            time.sleep(0.01)
            token = StreamingToken(
                token_id=i,
                decoded_text=f"tok_{i}",
                timestamp=time.time(),
                sequence_index=i
            )
            controller.publish_event(session.session_id, StreamingEvent(
                event_type=StreamingEventType.TOKEN_GENERATED,
                timestamp=time.time(),
                payload={"token": token}
            ))
        controller.complete_session(session.session_id, StreamCompletion.SUCCESS)

    t = threading.Thread(target=generator)
    t.start()

    tokens = list(emitter.stream())

    t.join()
    emitter.close()

    assert len(tokens) == 3
    assert tokens[0].decoded_text == "tok_0"
    assert tokens[2].decoded_text == "tok_2"

def test_cancellation():
    controller = StreamingController()
    session = controller.create_session()

    emitter = TokenEmitter()
    emitter.set_context(session.session_id, controller)
    controller.subscribe(session.session_id, emitter)

    # Simulate slow generation
    def generator():
        time.sleep(0.05)
        if session.is_active:
            token = StreamingToken(
                token_id=0,
                decoded_text="tok_0",
                timestamp=time.time(),
                sequence_index=0
            )
            controller.publish_event(session.session_id, StreamingEvent(
                event_type=StreamingEventType.TOKEN_GENERATED,
                timestamp=time.time(),
                payload={"token": token}
            ))

    t = threading.Thread(target=generator)
    t.start()

    # Cancel immediately
    controller.cancel_session(session.session_id)

    tokens = list(emitter.stream())
    t.join()
    emitter.close()

    assert len(tokens) == 0
    assert session.is_active is False
    stats = session.get_statistics()
    assert stats.tokens_emitted == 0

def test_multiple_concurrent_sessions():
    controller = StreamingController()

    def run_session(index):
        session = controller.create_session()
        emitter = TokenEmitter()
        emitter.set_context(session.session_id, controller)
        controller.subscribe(session.session_id, emitter)

        def generator():
            for i in range(5):
                token = StreamingToken(
                    token_id=i,
                    decoded_text=f"s{index}_t{i}",
                    timestamp=time.time(),
                    sequence_index=i
                )
                controller.publish_event(session.session_id, StreamingEvent(
                    event_type=StreamingEventType.TOKEN_GENERATED,
                    timestamp=time.time(),
                    payload={"token": token}
                ))
            controller.complete_session(session.session_id, StreamCompletion.SUCCESS)

        t = threading.Thread(target=generator)
        t.start()

        tokens = list(emitter.stream())
        t.join()
        emitter.close()

        assert len(tokens) == 5
        assert tokens[0].decoded_text == f"s{index}_t0"

    threads = []
    for i in range(10):
        t = threading.Thread(target=run_session, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def test_backpressure_drops_slow_consumer():
    controller = StreamingController()
    session = controller.create_session()

    # We make a transport with a very small buffer to trigger backpressure
    from omlx.runtime.streaming.transports import GeneratorTransport
    slow_emitter = GeneratorTransport(max_buffer_size=2)
    slow_emitter.set_context(session.session_id, controller)
    controller.subscribe(session.session_id, slow_emitter)

    # Push 5 tokens quickly. The queue only holds 2.
    for i in range(5):
        token = StreamingToken(
            token_id=i,
            decoded_text=f"tok_{i}",
            timestamp=time.time(),
            sequence_index=i
        )
        controller.publish_event(session.session_id, StreamingEvent(
            event_type=StreamingEventType.TOKEN_GENERATED,
            timestamp=time.time(),
            payload={"token": token}
        ))
        time.sleep(0.001)

    # Allow warning event thread to process
    time.sleep(0.1)

    # It should have been unsubscribed automatically
    assert slow_emitter not in controller._subscribers[session.session_id]

    # Verify the subscriber actually has the first 2 tokens in its queue
    tokens_in_queue = []
    while not slow_emitter._queue.empty():
        tokens_in_queue.append(slow_emitter._queue.get())

    assert len(tokens_in_queue) == 2
    assert tokens_in_queue[0].decoded_text == "tok_0"
    assert tokens_in_queue[1].decoded_text == "tok_1"


def test_replay_delivers_historical_events():
    controller = StreamingController()
    session = controller.create_session()

    # Generate 3 tokens without any subscribers
    for i in range(3):
        token = StreamingToken(
            token_id=i,
            decoded_text=f"tok_{i}",
            timestamp=time.time(),
            sequence_index=i
        )
        controller.publish_event(session.session_id, StreamingEvent(
            event_type=StreamingEventType.TOKEN_GENERATED,
            timestamp=time.time(),
            payload={"token": token}
        ))

    # Now subscribe an emitter with replay=True
    from omlx.runtime.streaming.transports import GeneratorTransport
    emitter = GeneratorTransport(max_buffer_size=10)
    emitter.set_context(session.session_id, controller)
    controller.subscribe(session.session_id, emitter, replay=True)

    # Generate 1 more token
    token = StreamingToken(
        token_id=3,
        decoded_text="tok_3",
        timestamp=time.time(),
        sequence_index=3
    )
    controller.publish_event(session.session_id, StreamingEvent(
        event_type=StreamingEventType.TOKEN_GENERATED,
        timestamp=time.time(),
        payload={"token": token}
    ))

    controller.complete_session(session.session_id, StreamCompletion.SUCCESS)

    # Emitter should have received all 4 tokens in order
    tokens = list(emitter.stream())

    assert len(tokens) == 4
    for i in range(4):
        assert tokens[i].token_id == i
        assert tokens[i].decoded_text == f"tok_{i}"


def test_transport_abstraction_usage():
    controller = StreamingController()
    session = controller.create_session()

    events_received = []
    def my_callback(event):
        events_received.append(event)

    from omlx.runtime.streaming.transports import CallbackTransport
    transport = CallbackTransport(my_callback, max_buffer_size=10)
    transport.start()

    controller.subscribe(session.session_id, transport)

    token = StreamingToken(
        token_id=0,
        decoded_text="tok_0",
        timestamp=time.time(),
        sequence_index=0
    )
    controller.publish_event(session.session_id, StreamingEvent(
        event_type=StreamingEventType.TOKEN_GENERATED,
        timestamp=time.time(),
        payload={"token": token}
    ))

    # Allow background thread to process callback
    time.sleep(0.05)
    transport.stop()

    # We should have received the token generated event
    # Filter for TOKEN_GENERATED since SESSION_STARTED is also stored when session is created
    token_events = [e for e in events_received if e.event_type == StreamingEventType.TOKEN_GENERATED]
    assert len(token_events) == 1
    assert token_events[0].payload["token"].decoded_text == "tok_0"
