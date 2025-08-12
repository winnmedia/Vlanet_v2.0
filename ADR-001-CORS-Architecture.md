# Architecture Decision Record: CORS Handling Strategy

**ADR-001**  
**Status**: Proposed  
**Date**: 2025-08-12  
**Author**: Arthur (Chief Architect)

## Title
Cross-Origin Resource Sharing (CORS) Architecture for VideoPlanet Platform

## Context and Problem Statement

The VideoPlanet platform consists of a React/Next.js frontend deployed on Vercel (https://vlanet.net) and a Django backend deployed on Railway (https://videoplanet.up.railway.app). The platform is experiencing persistent CORS issues preventing the frontend from accessing backend APIs, particularly authentication endpoints.

### Current Architecture Issues:
1. **Architectural Anti-pattern**: Using a Python HTTP server (`cors_server.py`) as a proxy to handle CORS, instead of proper Django middleware configuration
2. **Deployment Mismatch**: The `cors_server.py` returns 503 errors with mock responses, breaking actual functionality
3. **Configuration Fragmentation**: CORS configuration spread across multiple layers (cors_server.py, Django settings, middleware)
4. **Production Instability**: Railway deployment appears to be down or misconfigured
5. **Security Concerns**: Using wildcard origins (`*`) in some configurations

## Decision Drivers

1. **Security**: Must maintain strict origin validation in production
2. **Reliability**: CORS headers must be present on ALL responses (success, error, exceptions)
3. **Performance**: Minimal latency overhead from CORS handling
4. **Maintainability**: Single source of truth for CORS configuration
5. **Scalability**: Support for dynamic Vercel preview URLs
6. **Compliance**: Follow OWASP security guidelines for CORS

## Considered Options

### Option 1: Fix cors_server.py Proxy (Current Approach)
- **Pros**: Quick fix, already partially implemented
- **Cons**: 
  - Architectural anti-pattern
  - Additional point of failure
  - Performance overhead from proxy layer
  - Complexity in maintaining separate server

### Option 2: Native Django CORS with django-cors-headers
- **Pros**: 
  - Industry standard solution
  - Well-tested and maintained
  - Integrated with Django request/response cycle
  - Single configuration point
- **Cons**: 
  - Requires proper middleware ordering
  - Need to ensure error responses include headers

### Option 3: API Gateway/Reverse Proxy (Railway/Cloudflare)
- **Pros**: 
  - Centralized CORS handling
  - Platform-level solution
  - Can handle multiple backends
- **Cons**: 
  - Additional infrastructure cost
  - Platform lock-in
  - Configuration outside application code

### Option 4: Next.js API Routes as Proxy
- **Pros**: 
  - Same-origin requests (no CORS)
  - Frontend team control
  - Built-in Next.js rewrites
- **Cons**: 
  - Additional latency through Vercel
  - Complexity in handling auth tokens
  - Coupling frontend and backend deployments

## Decision Outcome

**Chosen Option: Option 2 - Native Django CORS with Enhanced Middleware**

### Justification:
1. **Architectural Coherence**: Aligns with Django best practices
2. **Single Responsibility**: Backend handles its own CORS policy
3. **Performance**: No additional proxy overhead
4. **Maintainability**: Configuration in one place (settings.py)
5. **Reliability**: Proven solution used by thousands of Django applications

## Implementation Strategy

### Phase 1: Immediate Stabilization (Day 1)
1. Remove cors_server.py from deployment pipeline
2. Properly configure django-cors-headers
3. Ensure middleware ordering is correct
4. Deploy with proper WSGI server (Gunicorn)

### Phase 2: Enhanced Error Handling (Day 2-3)
1. Create custom exception handler that guarantees CORS headers
2. Implement request ID tracking for debugging
3. Add comprehensive logging for CORS decisions

### Phase 3: Security Hardening (Week 1)
1. Implement strict origin validation
2. Add rate limiting per origin
3. Set up monitoring for CORS violations
4. Implement preflight caching strategy

## Technical Implementation

### 1. Correct Middleware Stack Order
```python
MIDDLEWARE = [
    # Security and health checks first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # CORS must be early in the stack
    'corsheaders.middleware.CorsMiddleware',
    
    # Session and common middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    # CSRF after CORS
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Authentication
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Messages and other middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom error handling last
    'config.middleware.GlobalErrorHandlingMiddleware',
]
```

### 2. CORS Configuration
```python
# Production CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://vlanet.net",
    "https://www.vlanet.net",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://vlanet-.*\.vercel\.app$",  # Vercel preview URLs
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Ensure headers on error responses
CORS_ALLOW_ALL_ORIGINS = False  # Never use in production
```

### 3. Deployment Configuration (Procfile)
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
release: python manage.py migrate
```

### 4. Railway Configuration (railway.json)
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/api/health/",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## Consequences

### Positive
- **Simplified Architecture**: Removal of unnecessary proxy layer
- **Better Performance**: Direct Django responses without proxy overhead
- **Improved Security**: Centralized origin validation
- **Enhanced Debugging**: Clear CORS decision logging
- **Platform Alignment**: Using Django ecosystem standards

### Negative
- **Migration Risk**: Need to carefully transition from current setup
- **Testing Requirements**: Comprehensive testing across all endpoints
- **Configuration Management**: Need to maintain allowed origins list

### Neutral
- **Documentation Need**: Team requires training on CORS configuration
- **Monitoring Setup**: Need to establish CORS metrics and alerts

## Risk Mitigation

1. **Rollback Plan**: Keep cors_server.py available for emergency rollback
2. **Gradual Migration**: Test with single endpoint before full deployment
3. **Monitoring**: Set up alerts for CORS errors in production
4. **Documentation**: Create runbook for CORS troubleshooting

## Validation Metrics

1. **Success Rate**: 0% CORS errors in production logs
2. **Performance**: <5ms overhead from CORS processing
3. **Security**: No unauthorized origin access
4. **Availability**: 99.9% uptime for API endpoints

## Migration Checklist

- [ ] Backup current configuration
- [ ] Update Django settings with proper CORS configuration
- [ ] Remove cors_server.py from Procfile
- [ ] Update railway.json with Gunicorn command
- [ ] Test locally with production-like setup
- [ ] Deploy to staging environment
- [ ] Validate all frontend API calls
- [ ] Monitor error rates for 24 hours
- [ ] Deploy to production
- [ ] Remove deprecated cors_server.py file

## References

- [Django CORS Headers Documentation](https://github.com/adamchainz/django-cors-headers)
- [OWASP CORS Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Origin_Resource_Sharing_Cheat_Sheet.html)
- [Railway Django Deployment Guide](https://docs.railway.app/guides/django)
- [Next.js API Routes Documentation](https://nextjs.org/docs/api-routes/introduction)

## Review and Sign-off

- **Architecture Review**: Pending
- **Security Review**: Pending
- **Operations Review**: Pending
- **Development Team Review**: Pending

---

**Next Steps**:
1. Review and approve this ADR
2. Create implementation tickets
3. Schedule deployment window
4. Prepare rollback procedures