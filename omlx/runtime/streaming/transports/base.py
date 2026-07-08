# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod
from typing import Optional, Any
from ..events import StreamingEvent
class BackpressureException(Exception): pass
class StreamingTransport(ABC):
    @abstractmethod
    def on_event(self, event: StreamingEvent) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass
