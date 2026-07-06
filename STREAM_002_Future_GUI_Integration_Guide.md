# STREAM-002: Future GUI Integration Guide

## Transport Registration
When GUI-001 is built, it should not interact with the compiler or runtime. Instead:
1. It should implement a `GUITransport(StreamingTransport)`.
2. It calls `get_controller().subscribe(session_id, my_gui_transport, replay=True)`.
3. If the GUI drops frames or lags, the `GUITransport` throws `BackpressureException`, protecting the AI inference engine.
