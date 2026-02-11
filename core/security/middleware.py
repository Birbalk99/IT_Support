"""
Multi-Level Security Middleware
Banking-Grade Security Implementation
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time

from core.config import settings
from core.logging.logger import security_logger
from core.security.rate_limiter import RateLimiter
from core.security.validators import validate_user_id, is_endpoint_allowed


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Multi-level security middleware
    Level 1: URL Whitelist validation
    Level 2: User ID validation
    Level 3: Rate limiting
    Level 4: Request validation
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process each request through security layers"""
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user_id from headers or query params
        user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id")
        
        # Security Level 1: URL Whitelist Check
        if settings.ENABLE_URL_WHITELIST:
            if not is_endpoint_allowed(request.url.path):
                security_logger.warning(
                    f"Unauthorized endpoint access attempt: {request.url.path}",
                    method=request.method,
                    extra_info={"ip": client_ip, "user_id": user_id}
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Access to this endpoint is not allowed"}
                )
        
        # Security Level 2: User ID Validation (Skip for public endpoints)
        if settings.ENABLE_USER_ID_VALIDATION:
            # Check if endpoint requires authentication
            if not self._is_public_endpoint(request.url.path):
                if not user_id:
                    security_logger.warning(
                        f"Missing user_id for protected endpoint: {request.url.path}",
                        method=request.method,
                        extra_info={"ip": client_ip}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "User ID is required for this endpoint"}
                    )
                
                # Validate user_id format and existence
                is_valid, error_msg = validate_user_id(user_id)
                if not is_valid:
                    security_logger.warning(
                        f"Invalid user_id: {error_msg}",
                        method=request.method,
                        extra_info={"ip": client_ip, "user_id": user_id}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": error_msg}
                    )
        
        # Security Level 3: Rate Limiting
        if settings.RATE_LIMIT_ENABLED:
            identifier = user_id or client_ip
            is_allowed, retry_after = self.rate_limiter.is_allowed(identifier)
            
            if not is_allowed:
                security_logger.warning(
                    f"Rate limit exceeded",
                    method=request.method,
                    extra_info={"ip": client_ip, "user_id": user_id}
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": f"Rate limit exceeded. Retry after {retry_after} seconds"},
                    headers={"Retry-After": str(retry_after)}
                )
        
        # Security Level 4: Request Size and Content Type Validation
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            security_logger.warning(
                f"Request size too large: {content_length} bytes",
                method=request.method,
                extra_info={"ip": client_ip, "user_id": user_id}
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request size exceeds maximum allowed limit"}
            )
        
        # Add user_id to request state for downstream use
        request.state.user_id = user_id
        request.state.client_ip = client_ip
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log successful request
            process_time = time.time() - start_time
            security_logger.info(
                f"Request processed successfully",
                method=request.method,
                extra_info={
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.2f}s",
                    "user_id": user_id,
                    "ip": client_ip
                }
            )
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            return response
            
        except Exception as e:
            security_logger.error(
                f"Request processing error: {str(e)}",
                method=request.method,
                extra_info={"path": request.url.path, "user_id": user_id, "ip": client_ip}
            )
            raise
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (doesn't require user_id)"""
        public_endpoints = [
            "/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/auth/login",
            "/api/auth/register",
        ]
        return any(path.startswith(endpoint) for endpoint in public_endpoints)
