import sqlite3
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

import logging

logger = logging.getLogger(__name__)

class CacheUpdateMiddleware(MiddlewareMixin):
    """
    Middleware to check if the cache needs to be updated based on a content version
    stored in the database. If the cached content version does not match the database version,
    the cache is cleared and updated with the latest version.
    
    Make sure that this is the middleware sequence:
    
    MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    
    "admin_base.middleware.CacheUpdateMiddleware",
    
    ...
    ]
    
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        logger.info("CacheUpdateMiddleware is running.")
        
        cache_status, key, value = self.reset_cache()
        
        if cache_status == True:
            cache.clear()
            cache.set(key, value)

        response = self.get_response(request)    
            
        return response
    
    def reset_cache(self):
        """
        Checks if the cache version stored in the database is different from the cache version
        stored in the user's session. If different, the cache is considered outdated and needs
        to be updated.
        
        Returns:
            tuple:
                - bool: Whether the cache should be reset (True if cache versions don't match).
                - str: The cache key to store the latest version.
                - str: The new cache version value to be set.
        """
        conn = sqlite3.connect('admin_base/general.db')  # Update the path accordingly
        cursor = conn.cursor()

        # Fetch the current content_update_index from the database
        cursor.execute('SELECT content_update_index FROM update_index')
        cache_version = cursor.fetchone()[0]
        conn.close()

        # Check if the user has cached data and a cache_index stored
        cache_key = f"latest_cache_index"
        session_cache_version = cache.get(cache_key)
        
        if session_cache_version is None or session_cache_version != cache_version:
            print("Reseted Cache")
            return True, "latest_cache_index", cache_version
        
        else:
            print("No Cache Reset")
            return False, '', ''
        