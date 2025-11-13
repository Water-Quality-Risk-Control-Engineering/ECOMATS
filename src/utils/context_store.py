#!/usr/bin/env python3
from typing import Any, Dict
import threading

class ContextStore:
    _store: Dict[str, Any] = {}
    _lock = threading.RLock()

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        with cls._lock:
            cls._store[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        with cls._lock:
            return cls._store.get(key, default)

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._store.clear()

