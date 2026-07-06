# SPDX-License-Identifier: Apache-2.0
"""
Global Observer for simple usage.
"""
import threading
from .observer import Observer

_local_observer = threading.local()

def get_observer() -> Observer:
    """Gets the thread-local observer, creating one if it doesn't exist."""
    if not hasattr(_local_observer, "observer"):
        _local_observer.observer = Observer()
    return _local_observer.observer

def set_observer(observer: Observer):
    """Sets the thread-local observer."""
    _local_observer.observer = observer

def reset_observer():
    """Resets the thread-local observer."""
    if hasattr(_local_observer, "observer"):
        del _local_observer.observer
