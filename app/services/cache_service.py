import redis
import pickle
import hashlib
from typing import Any, Optional


class CacheService:
    """Redis-based caching service"""
    
    def __init__(self, redis_url: str):
        print(f"💾 Connecting to Redis at {redis_url}...")
        try:
            self.redis_client = redis.from_url(
                redis_url, 
                decode_responses=False
            )
            self.redis_client.ping()
            print("✅ Redis connected successfully!")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   Caching will be disabled.")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (seconds)"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                key,
                ttl,
                pickle.dumps(value)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    def clear_all(self):
        """Clear all cache"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.flushdb()
            print("✅ Cache cleared!")
        except Exception as e:
            print(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            info = self.redis_client.info()
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            
            return {
                "total_keys": self.redis_client.dbsize(),
                "memory_used": info.get("used_memory_human"),
                "hits": hits,
                "misses": misses,
                "hit_rate": hits / total if total > 0 else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def generate_cache_key(text: str, prefix: str = "query") -> str:
        """Generate a cache key from text"""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return f"{prefix}:{text_hash}"