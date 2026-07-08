# SPDX-License-Identifier: Apache-2.0
import queue
import threading
from typing import Callable
import time
from .base import StreamingTransport, BackpressureException
from ..events import StreamingEvent
class CallbackTransport(StreamingTransport):
    def __init__(self, callback: Callable[[StreamingEvent], None], max_buffer_size: int = 1000):
        self.callback = callback
        self.max_buffer_size = max_buffer_size
        self._queue = queue.Queue(maxsize=max_buffer_size)
        self._thread = None
        self._running = False
    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._queue.put(None)
            self._thread.join(timeout=1.0)
    def on_event(self, event: StreamingEvent) -> None:
        if not self._running: return
        try:
            self._queue.put(event, block=True, timeout=0.01)
        except queue.Full:
            raise BackpressureException(f"CallbackTransport buffer full")
    def _worker(self):
        while self._running:
            try:
                event = self._queue.get(timeout=0.1)
                if event is None: break
                try: self.callback(event)
                except Exception: pass
                finally: self._queue.task_done()
            except queue.Empty: continue
