#!/usr/bin/env python3
"""
上下文存储 - 带TTL支持的线程安全缓存
用于多智能体系统中的跨Agent数据共享
"""
from typing import Any, Dict, Optional, Tuple
import threading
import time

# 默认TTL: 30分钟 (足够完成一次完整的材料设计流程)
DEFAULT_TTL = 1800

class ContextStore:
    """带TTL支持的全局上下文存储"""
    _store: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expire_time)
    _lock = threading.RLock()

    @classmethod
    def set(cls, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒)，默认30分钟
        """
        expire_time = time.time() + (ttl if ttl is not None else DEFAULT_TTL)
        with cls._lock:
            cls._store[key] = (value, expire_time)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取缓存值，如果过期则返回默认值
        
        Args:
            key: 缓存键
            default: 默认值
        
        Returns:
            缓存值或默认值
        """
        with cls._lock:
            if key not in cls._store:
                return default
            value, expire_time = cls._store[key]
            if time.time() > expire_time:
                del cls._store[key]
                return default
            return value

    @classmethod
    def clear(cls) -> None:
        """清除所有缓存"""
        with cls._lock:
            cls._store.clear()
    
    @classmethod
    def cleanup_expired(cls) -> int:
        """
        清理所有过期项
        
        Returns:
            清理的条目数
        """
        with cls._lock:
            now = time.time()
            expired_keys = [k for k, (_, exp) in cls._store.items() if now > exp]
            for key in expired_keys:
                del cls._store[key]
            return len(expired_keys)
    
    @classmethod
    def size(cls) -> int:
        """返回缓存大小"""
        with cls._lock:
            return len(cls._store)

