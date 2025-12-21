#!/usr/bin/env python3
# Context storage for thread-safe data sharing / 线程安全的上下文存储
from typing import Any, Dict
import threading

class ContextStore:
    """Thread-safe context storage for sharing data across agents
    线程安全的上下文存储，用于在智能体之间共享数据
    """
    _store: Dict[str, Any] = {}
    _lock = threading.RLock()

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a value in the context store / 在上下文存储中设置值"""
        with cls._lock:
            cls._store[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from the context store / 从上下文存储中获取值"""
        with cls._lock:
            return cls._store.get(key, default)

    @classmethod
    def clear(cls) -> None:
        """Clear all values from the context store / 清除上下文存储中的所有值"""
        with cls._lock:
            cls._store.clear()

