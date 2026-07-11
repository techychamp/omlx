# SPDX-License-Identifier: Apache-2.0
"""
Backend Lifecycle Metadata.
"""
import enum

class BackendLifecycleState(str, enum.Enum):
    REGISTERED = "REGISTERED"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    INITIALIZING = "INITIALIZING"
    DEPRECATED = "DEPRECATED"
    EXPERIMENTAL = "EXPERIMENTAL"
    DISABLED = "DISABLED"
    PLUGIN = "PLUGIN"
