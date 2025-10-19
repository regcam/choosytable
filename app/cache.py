"""
Improved caching module for ChoosyTable
Provides better cache key management, race condition handling, and invalidation strategies
"""

import hashlib
import logging
from functools import wraps
from typing import Any, Optional, List, Dict
from pymemcache.client.base import PooledClient
from bson import json_util

logger = logging.getLogger(__name__)

class CacheManager:
    """Enhanced cache manager with better key management and error handling"""
    
    def __init__(self, client: PooledClient):
        self.client = client
        self.key_prefix = "choosytable:"
        
    def _generate_key(self, base_key: str, *args, **kwargs) -> str:
        """Generate a consistent cache key with optional parameters"""
        key_parts = [self.key_prefix, base_key]
        
        # Add positional arguments
        for arg in args:
            key_parts.append(str(arg))
            
        # Add keyword arguments in sorted order for consistency
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
            
        full_key = "_".join(key_parts)
        
        # Hash very long keys to avoid memcached key length limits
        if len(full_key) > 200:
            key_hash = hashlib.md5(full_key.encode()).hexdigest()
            full_key = f"{self.key_prefix}hashed:{key_hash}"
            
        return full_key
    
    def get(self, base_key: str, *args, **kwargs) -> Optional[Any]:
        """Safely get a cached value"""
        try:
            cache_key = self._generate_key(base_key, *args, **kwargs)
            return self.client.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get failed for key {base_key}: {e}")
            return None
    
    def set(self, base_key: str, value: Any, ttl: int = 3600, *args, **kwargs) -> bool:
        """Safely set a cached value with TTL"""
        try:
            cache_key = self._generate_key(base_key, *args, **kwargs)
            return self.client.set(cache_key, value, expire=ttl)
        except Exception as e:
            logger.warning(f"Cache set failed for key {base_key}: {e}")
            return False
    
    def delete(self, base_key: str, *args, **kwargs) -> bool:
        """Safely delete a cached value"""
        try:
            cache_key = self._generate_key(base_key, *args, **kwargs)
            return self.client.delete(cache_key)
        except Exception as e:
            logger.warning(f"Cache delete failed for key {base_key}: {e}")
            return False
    
    def delete_multiple(self, keys: List[Dict]) -> bool:
        """Delete multiple cache keys safely"""
        success = True
        for key_info in keys:
            base_key = key_info.get('base_key')
            args = key_info.get('args', [])
            kwargs = key_info.get('kwargs', {})
            if not self.delete(base_key, *args, **kwargs):
                success = False
        return success
    
    def invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate all cache keys related to a specific user"""
        cache_keys = [
            {'base_key': 'user_reviews', 'args': [user_id]},
            {'base_key': 'user_by_email', 'args': [user_id]},
        ]
        self.delete_multiple(cache_keys)
    
    def invalidate_company_cache(self, company_id: str) -> None:
        """Invalidate all cache keys related to a specific company"""
        cache_keys = [
            {'base_key': 'company_data', 'args': [company_id]},
            {'base_key': 'company_interviews', 'args': [company_id]},
            {'base_key': 'all_reviews'},  # This affects the global reviews list
        ]
        self.delete_multiple(cache_keys)

def cached_query(cache_manager: CacheManager, base_key: str, ttl: int = 3600):
    """Decorator for caching query results with automatic key generation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get from cache first
            cached_result = cache_manager.get(base_key, *args, **kwargs)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(base_key, result, ttl, *args, **kwargs)
            
            return result
        return wrapper
    return decorator

class DatabaseCache:
    """Database-specific caching utilities"""
    
    def __init__(self, cache_manager: CacheManager, collection):
        self.cache = cache_manager
        self.collection = collection
    
    @cached_query(cache_manager=None, base_key="user_by_email", ttl=1800)  # 30 minutes
    def find_user_by_email(self, email: str):
        """Cached user lookup by email"""
        self.cache = cache_manager  # Will be set when called
        return self.collection.find_one({'email': email})
    
    @cached_query(cache_manager=None, base_key="user_reviews", ttl=900)  # 15 minutes
    def find_user_reviews(self, user_id: str):
        """Cached user reviews lookup"""
        self.cache = cache_manager
        return list(
            self.collection.find(
                {'reviews.user': user_id},
                {'reviews': 1, '_id': 1, 'company': 1}
            ).sort('last_modified', -1)
        )
    
    @cached_query(cache_manager=None, base_key="all_reviews", ttl=600)  # 10 minutes
    def find_all_reviews(self):
        """Cached lookup of all companies with reviews"""
        self.cache = cache_manager
        return list(
            self.collection.find(
                {'reviews': {"$exists": True}},
                {'company': 1, 'reviews': 1, 'last_modified': 1}  # Only fetch needed fields
            ).sort('last_modified', -1)
        )
    
    @cached_query(cache_manager=None, base_key="company_data", ttl=1800)  # 30 minutes  
    def find_company_by_id(self, company_id: str):
        """Cached company lookup by ID"""
        self.cache = cache_manager
        from bson import ObjectId
        return self.collection.find_one({'_id': ObjectId(company_id)})

# Cache invalidation helpers
def invalidate_on_user_update(cache_manager: CacheManager, user_id: str):
    """Invalidate caches when user data changes"""
    cache_manager.invalidate_user_cache(user_id)

def invalidate_on_review_update(cache_manager: CacheManager, user_id: str, company_id: str):
    """Invalidate caches when reviews are added/updated"""
    cache_manager.invalidate_user_cache(user_id)
    cache_manager.invalidate_company_cache(company_id)

def invalidate_on_company_update(cache_manager: CacheManager, company_id: str):
    """Invalidate caches when company data changes"""
    cache_manager.invalidate_company_cache(company_id)