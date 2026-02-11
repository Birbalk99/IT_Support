"""
Rate Limiter
Implements rate limiting to prevent abuse
"""
import time
from typing import Dict, Tuple
from collections import defaultdict
from threading import Lock

from core.config import settings


class RateLimiter:
    """
    In-memory rate limiter
    For production, consider using Redis for distributed rate limiting
    """
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
        self._max_requests = settings.RATE_LIMIT_PER_MINUTE
        self._window_seconds = 60
    
    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if request is allowed based on rate limit
        
        Args:
            identifier: Unique identifier (user_id or IP address)
            
        Returns:
            Tuple[bool, int]: (is_allowed, retry_after_seconds)
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - self._window_seconds
            
            # Clean old requests outside the current window
            self._requests[identifier] = [
                req_time for req_time in self._requests[identifier]
                if req_time > window_start
            ]
            
            # Check if rate limit exceeded
            if len(self._requests[identifier]) >= self._max_requests:
                oldest_request = min(self._requests[identifier])
                retry_after = int(oldest_request + self._window_seconds - current_time) + 1
                return False, retry_after
            
            # Add current request
            self._requests[identifier].append(current_time)
            return True, 0
    
    def reset(self, identifier: str):
        """Reset rate limit for an identifier"""
        with self._lock:
            if identifier in self._requests:
                del self._requests[identifier]
    
    def cleanup(self):
        """Clean up old entries to prevent memory bloat"""
        with self._lock:
            current_time = time.time()
            window_start = current_time - self._window_seconds
            
            identifiers_to_delete = []
            for identifier, requests in self._requests.items():
                # Remove old requests
                self._requests[identifier] = [
                    req_time for req_time in requests
                    if req_time > window_start
                ]
                
                # Mark empty entries for deletion
                if not self._requests[identifier]:
                    identifiers_to_delete.append(identifier)
            
            # Delete empty entries
            for identifier in identifiers_to_delete:
                del self._requests[identifier]
