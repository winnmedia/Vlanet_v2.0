"""
Optimized logging configuration for production
"""
import os

def get_logging_config(debug=False):
    """Get optimized logging configuration"""
    
    # Production logging levels
    log_levels = {
        'django': 'WARNING',
        'django.request': 'ERROR',
        'django.db.backends': 'ERROR',
        'django.security': 'ERROR',
        'users': 'WARNING',
        'projects': 'WARNING',
        'feedbacks': 'WARNING',
        'video_planning': 'WARNING',
    }
    
    if debug:
        # Development mode - more verbose
        log_levels.update({
            'django': 'INFO',
            'django.request': 'INFO',
            'users': 'INFO',
        })
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'rate_limit': {
                '()': 'django.utils.log.CallbackFilter',
                'callback': lambda record: should_log(record),
            },
        },
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(levelname)s %(asctime)s %(name)s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose' if debug else 'simple',
                'filters': ['rate_limit'],
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': '/tmp/django_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'verbose',
                'level': 'ERROR',
                'filters': ['require_debug_false'],
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            name: {
                'handlers': ['console'] + (['error_file'] if name == 'django.request' else []),
                'level': level,
                'propagate': False,
            }
            for name, level in log_levels.items()
        },
    }

# Rate limiting for logs
_log_counts = {}

def should_log(record):
    """Rate limit logs to prevent overflow"""
    import time
    
    key = f"{record.name}:{record.levelno}"
    now = time.time()
    
    if key not in _log_counts:
        _log_counts[key] = {'count': 0, 'reset_time': now + 1}
    
    if now > _log_counts[key]['reset_time']:
        _log_counts[key] = {'count': 1, 'reset_time': now + 1}
        return True
    
    _log_counts[key]['count'] += 1
    
    # Allow max 10 logs per second per logger/level
    return _log_counts[key]['count'] <= 10