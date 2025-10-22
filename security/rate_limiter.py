"""
RATE LIMITER - Enterprise API rate limiting
"""
# security/rate_limiter.py
import time
from typing import Dict
from fastapi import HTTPException

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    async def check_rate_limit(self, identifier: str, limit: int, window: int):
        """Check if request is within rate limits"""
        now = time.time()
        window_start = now - window
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > window_start
        ]
        
        if len(self.requests[identifier]) >= limit:
            raise HTTPException(429, "Rate limit exceeded")
        
        self.requests[identifier].append(now)

# security/input_sanitizer.py
import html
import re

def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;\\/*?|&<>$]', '', input_string)
    # HTML escape
    sanitized = html.escape(sanitized)
    return sanitized.strip()
import time
from typing import Dict, List
from fastapi import HTTPException, status

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
    
    async def check_rate_limit(self, identifier: str, limit: int, window: int):
        """
        Check if request is within rate limits
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            limit: Maximum number of requests in window
            window: Time window in seconds
        """
        now = time.time()
        window_start = now - window
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests outside current window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. {limit} requests per {window} seconds allowed."
            )
        
        # Add current request
        self.requests[identifier].append(now)
        
        # Clean up old identifiers periodically (simplified)
        if len(self.requests) > 1000:  # Prevent memory leaks
            old_identifiers = [
                ident for ident, times in self.requests.items()
                if not times or max(times) < now - 3600  # 1 hour old
            ]
            for ident in old_identifiers:
                del self.requests[ident]
