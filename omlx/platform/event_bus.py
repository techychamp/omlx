# SPDX-License-Identifier: Apache-2.0
from dataclasses import dataclass, field
import datetime
import uuid
import logging
from typing import Callable, DefaultDict, List, Dict, Any
from collections import defaultdict

logger = logging.getLogger("omlx.platform.bus")

@dataclass(frozen=True)
class PlatformEvent:
    name: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: dict = field(default_factory=dict)

@dataclass(frozen=True)
class PlatformCommand:
    name: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: dict = field(default_factory=dict)

class PlatformEventBus:
    def __init__(self) -> None:
        self._listeners: DefaultDict[str, List[Callable[[PlatformEvent], None]]] = defaultdict(list)
        self._command_handlers: Dict[str, Callable[[PlatformCommand], None]] = {}
        self._query_handlers: Dict[str, Callable[[Any], Any]] = {}
        self._events: List[PlatformEvent] = []

    def subscribe(self, event_name: str, listener: Callable[[PlatformEvent], None]) -> None:
        self._listeners[event_name].append(listener)

    def publish(self, event: PlatformEvent) -> None:
        self._events.append(event)
        logger.debug("Publishing event %s: %s", event.name, event.data)
        for listener in list(self._listeners[event.name]):
            try:
                listener(event)
            except Exception as e:
                logger.error("Error in event listener for %s: %s", event.name, e)
        for listener in list(self._listeners["*"]):
            try:
                listener(event)
            except Exception as e:
                logger.error("Error in wildcard listener: %s", e)

    def register_command(self, command_name: str, handler: Callable[[PlatformCommand], None]) -> None:
        self._command_handlers[command_name] = handler

    def send_command(self, command: PlatformCommand) -> None:
        logger.debug("Sending command %s: %s", command.name, command.data)
        handler = self._command_handlers.get(command.name)
        if handler:
            try:
                handler(command)
            except Exception as e:
                logger.error("Error executing command handler for %s: %s", command.name, e)
        else:
            logger.warning("No handler registered for command %s", command.name)

    def register_query(self, query_name: str, handler: Callable[[Any], Any]) -> None:
        self._query_handlers[query_name] = handler

    def query(self, query_name: str, params: Any = None) -> Any:
        logger.debug("Executing query %s with params: %s", query_name, params)
        handler = self._query_handlers.get(query_name)
        if handler:
            try:
                return handler(params)
            except Exception as e:
                logger.error("Error executing query handler for %s: %s", query_name, e)
                raise
        else:
            logger.warning("No handler registered for query %s", query_name)
            return None
