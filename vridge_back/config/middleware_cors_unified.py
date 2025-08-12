"""
Unified CORS Middleware for VideoPlanet
Arthur, Chief Architect - 2025-08-12

This single middleware handles ALL CORS requirements:
- Preflight OPTIONS requests
- Regular requests (GET, POST, etc.)
- Error responses (4xx, 5xx)
- WebSocket upgrades
- Health checks

Design Principles:
- Single Responsibility: Only CORS handling
- Fail-Safe: Always adds headers when needed
- Performance: Minimal overhead, early exit for OPTIONS
- Observability: Structured logging with request IDs
"""

import logging
import uuid
from typing import Optional, Set, List
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import re

logger = logging.getLogger('django.cors')


class UnifiedCORSMiddleware(MiddlewareMixin):
    """
    Unified CORS middleware that guarantees headers on all responses.
    
    This middleware should be the FIRST in the MIDDLEWARE stack to ensure
    it processes all requests and responses, including error cases.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
        # Pre-compile configuration for performance
        self.allowed_origins: Set[str] = set(
            getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        )
        
        self.allowed_regex_patterns: List[re.Pattern] = [
            re.compile(pattern) for pattern in 
            getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])
        ]
        
        self.allow_all_origins: bool = getattr(
            settings, 'CORS_ALLOW_ALL_ORIGINS', False
        )
        
        self.allow_credentials: bool = getattr(
            settings, 'CORS_ALLOW_CREDENTIALS', True
        )
        
        self.allowed_methods: str = ', '.join(
            getattr(settings, 'CORS_ALLOW_METHODS', [
                'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'HEAD'
            ])
        )
        
        self.allowed_headers: str = ', '.join(
            getattr(settings, 'CORS_ALLOW_HEADERS', [
                'accept', 'accept-encoding', 'authorization', 'content-type',
                'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
                'cache-control', 'pragma', 'x-idempotency-key', 'x-request-id'
            ])
        )
        
        self.expose_headers: str = ', '.join(
            getattr(settings, 'CORS_EXPOSE_HEADERS', [
                'Content-Type', 'X-CSRFToken', 'X-Request-ID', 'Authorization'
            ])
        )
        
        self.preflight_max_age: str = str(
            getattr(settings, 'CORS_PREFLIGHT_MAX_AGE', 86400)
        )
        
        logger.info(
            f"UnifiedCORSMiddleware initialized: "
            f"allowed_origins={len(self.allowed_origins)}, "
            f"regex_patterns={len(self.allowed_regex_patterns)}, "
            f"allow_all={self.allow_all_origins}"
        )
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle preflight OPTIONS requests immediately.
        Add request ID for tracing.
        """
        # Add request ID for tracing
        if not hasattr(request, 'id'):
            request.id = str(uuid.uuid4())[:8]
        
        # Log incoming request
        origin = request.META.get('HTTP_ORIGIN', 'no-origin')
        logger.debug(
            f"[{request.id}] {request.method} {request.path} from {origin}"
        )
        
        # Handle preflight OPTIONS immediately
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response.status_code = 200
            response['Content-Length'] = '0'
            
            # Add CORS headers
            self._add_cors_headers(request, response, is_preflight=True)
            
            logger.info(
                f"[{request.id}] Preflight OPTIONS handled for {origin}"
            )
            
            return response
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Ensure CORS headers are present on all responses.
        """
        # Skip if already handled (e.g., OPTIONS in process_request)
        if request.method == 'OPTIONS' and response.status_code == 200:
            return response
        
        # Add CORS headers to all responses
        self._add_cors_headers(request, response, is_preflight=False)
        
        # Log response
        logger.debug(
            f"[{getattr(request, 'id', 'unknown')}] "
            f"Response {response.status_code} with CORS headers"
        )
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """
        Log exceptions but don't handle them - let Django's error handling
        create the response, then we'll add CORS headers in process_response.
        """
        logger.error(
            f"[{getattr(request, 'id', 'unknown')}] "
            f"Exception in view: {exception.__class__.__name__}: {exception}",
            exc_info=True
        )
        # Return None to let other middleware and Django handle the exception
        return None
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Check if the origin is allowed based on configuration.
        """
        if not origin:
            return False
        
        # Allow all origins if configured
        if self.allow_all_origins:
            return True
        
        # Check exact match
        if origin in self.allowed_origins:
            return True
        
        # Check regex patterns
        for pattern in self.allowed_regex_patterns:
            if pattern.match(origin):
                return True
        
        # In DEBUG mode, allow localhost
        if settings.DEBUG:
            if origin.startswith(('http://localhost:', 'http://127.0.0.1:')):
                return True
        
        return False
    
    def _add_cors_headers(
        self, 
        request: HttpRequest, 
        response: HttpResponse, 
        is_preflight: bool = False
    ) -> None:
        """
        Add appropriate CORS headers to the response.
        """
        origin = request.META.get('HTTP_ORIGIN', '')
        
        # Always add Vary header
        vary_headers = response.get('Vary', '')
        if vary_headers:
            vary_headers = f"{vary_headers}, Origin"
        else:
            vary_headers = "Origin"
        response['Vary'] = vary_headers
        
        # Check if origin is allowed
        if self._is_origin_allowed(origin):
            # Add allowed origin
            response['Access-Control-Allow-Origin'] = origin
            
            # Add credentials if configured
            if self.allow_credentials:
                response['Access-Control-Allow-Credentials'] = 'true'
            
            # Add expose headers
            response['Access-Control-Expose-Headers'] = self.expose_headers
            
            # Add preflight-specific headers
            if is_preflight:
                response['Access-Control-Allow-Methods'] = self.allowed_methods
                response['Access-Control-Allow-Headers'] = self.allowed_headers
                response['Access-Control-Max-Age'] = self.preflight_max_age
            
            logger.debug(
                f"[{getattr(request, 'id', 'unknown')}] "
                f"CORS headers added for allowed origin: {origin}"
            )
        else:
            # Log rejected origin
            if origin:
                logger.warning(
                    f"[{getattr(request, 'id', 'unknown')}] "
                    f"CORS rejected origin: {origin}"
                )
        
        # Always add request ID for tracing
        if hasattr(request, 'id'):
            response['X-Request-ID'] = request.id


class CORSDebugMiddleware(MiddlewareMixin):
    """
    Debug middleware to log CORS-related information.
    This should be placed AFTER UnifiedCORSMiddleware in development.
    """
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Log CORS headers for debugging."""
        if settings.DEBUG:
            cors_headers = {
                key: value for key, value in response.items()
                if key.startswith('Access-Control-') or key == 'Vary'
            }
            
            if cors_headers:
                logger.debug(
                    f"[{getattr(request, 'id', 'unknown')}] "
                    f"CORS headers on response: {cors_headers}"
                )
        
        return response