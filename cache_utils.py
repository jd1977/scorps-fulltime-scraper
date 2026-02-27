#!/usr/bin/env python3
"""
Simple in-memory caching utilities
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from app_config import CACHE_TTL_MINUTES


class SimpleCache:
    """Simple in-memory cache with TTL (Time To Live)"""
    
    def __init__(self, ttl_minutes: int = CACHE_TTL_MINUTES):
        """
        Initialize cache
        
        Args:
            ttl_minutes: Time to live in minutes
        """
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Check if expired
        if datetime.now() - timestamp > self._ttl:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, datetime.now())
    
    def clear(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
    
    def remove(self, key: str) -> None:
        """
        Remove specific key from cache
        
        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]
    
    def size(self) -> int:
        """Get number of items in cache"""
        return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache
        
        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self._ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
