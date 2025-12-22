#!/usr/bin/env python3
# Context storage for thread-safe data sharing
from typing import Any, Dict
import threading

class ContextStore:
    """Thread-safe context storage for sharing data across agents."""
    _store: Dict[str, Any] = {}
    _lock = threading.RLock()

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a value in the context store."""
        with cls._lock:
            cls._store[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from the context store."""
        with cls._lock:
            return cls._store.get(key, default)

    @classmethod
    def clear(cls) -> None:
        """Clear all values from the context store."""
        with cls._lock:
            cls._store.clear()

