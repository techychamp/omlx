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

    emitter = TokenEmitter(session, controller)

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

    emitter = TokenEmitter(session, controller)

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
        emitter = TokenEmitter(session, controller)

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
