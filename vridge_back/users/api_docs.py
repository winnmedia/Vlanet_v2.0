"""
OpenAPI/Swagger Documentation for VideoPlanet Authentication API
Comprehensive API documentation with examples and schemas
"""

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status


# Common response schemas
def get_error_response_schema():
    """Standard error response schema"""
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
            'status': openapi.Schema(type=openapi.TYPE_STRING, default='error'),
            'error': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'code': openapi.Schema(type=openapi.TYPE_STRING, description='Error code'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Human readable error message'),
                    'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='HTTP status code'),
                    'details': openapi.Schema(type=openapi.TYPE_OBJECT, description='Additional error details (optional)')
                }
            ),
            'timestamp': openapi.Schema(type=openapi.TYPE_NUMBER, description='Response timestamp'),
            'request_id': openapi.Schema(type=openapi.TYPE_STRING, description='Unique request identifier for tracing'),
            'performance': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'response_time_ms': openapi.Schema(type=openapi.TYPE_NUMBER, description='Response time in milliseconds')
                }
            )
        }
    )


def get_success_response_schema(data_schema=None):
    """Standard success response schema"""
    properties = {
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
        'status': openapi.Schema(type=openapi.TYPE_STRING, default='success'),
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
        'timestamp': openapi.Schema(type=openapi.TYPE_NUMBER, description='Response timestamp'),
        'request_id': openapi.Schema(type=openapi.TYPE_STRING, description='Unique request identifier'),
        'performance': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'response_time_ms': openapi.Schema(type=openapi.TYPE_NUMBER, description='Response time in milliseconds')
            }
        )
    }
    
    if data_schema:
        properties['data'] = data_schema
    
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties)


# User data schema
user_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email address'),
        'nickname': openapi.Schema(type=openapi.TYPE_STRING, description='Display name'),
        'login_method': openapi.Schema(type=openapi.TYPE_STRING, enum=['email', 'google', 'kakao', 'naver']),
        'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Email verification status'),
        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Account active status'),
        'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
        'last_login': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
    }
)

# Login response data schema
login_response_data_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access_token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
        'vridge_session': openapi.Schema(type=openapi.TYPE_STRING, description='Session token (compatibility)'),
        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Legacy access token field'),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Legacy refresh token field'),
        'user': user_data_schema,
        'expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Token expiry time in seconds')
    }
)


# Swagger decorators for API views
login_swagger_schema = swagger_auto_schema(
    operation_id='user_login',
    operation_summary='User Login',
    operation_description='''
    Authenticate user with email/username and password.
    
    This endpoint:
    - Supports login with both email address and username
    - Returns JWT access and refresh tokens
    - Includes user profile information
    - Implements rate limiting (5 attempts per minute)
    - Provides detailed error responses
    - Monitors performance (target <200ms)
    
    Rate Limits:
    - 5 login attempts per minute per IP/email combination
    - 10 login attempts per 5 minutes per IP/email combination
    
    Performance:
    - Target response time: <200ms
    - Automatic performance monitoring and logging
    ''',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Email address or username',
                example='user@example.com'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='password',
                description='User password (minimum 6 characters)',
                example='password123'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=get_success_response_schema(login_response_data_schema),
            examples={
                'application/json': {
                    'success': True,
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'vridge_session': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 1,
                            'username': 'testuser',
                            'email': 'user@example.com',
                            'nickname': 'Test User',
                            'login_method': 'email',
                            'email_verified': True,
                            'is_active': True,
                            'date_joined': '2025-08-11T12:00:00Z',
                            'last_login': '2025-08-11T12:30:00Z'
                        },
                        'expires_in': 3600
                    },
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345',
                    'performance': {
                        'response_time_ms': 150.5
                    }
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - validation error',
            schema=get_error_response_schema(),
            examples={
                'application/json': {
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid login credentials format',
                        'status': 400,
                        'details': {
                            'email': ['This field is required.'],
                            'password': ['This field is required.']
                        }
                    },
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345'
                }
            }
        ),
        401: openapi.Response(
            description='Unauthorized - invalid credentials',
            schema=get_error_response_schema(),
            examples={
                'application/json': {
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'INVALID_CREDENTIALS',
                        'message': 'Invalid email or password',
                        'status': 401
                    },
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345'
                }
            }
        ),
        403: openapi.Response(
            description='Forbidden - account inactive or email not verified',
            schema=get_error_response_schema(),
            examples={
                'application/json': {
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'EMAIL_NOT_VERIFIED',
                        'message': 'Email verification required. Please check your email for verification link.',
                        'status': 403,
                        'details': {
                            'email': 'user@example.com',
                            'verification_required': True
                        }
                    },
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345'
                }
            }
        ),
        429: openapi.Response(
            description='Too many requests - rate limit exceeded',
            schema=get_error_response_schema(),
            examples={
                'application/json': {
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Too many login attempts. Please try again in 5 minutes.',
                        'status': 429,
                        'retry_after': 300
                    },
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345'
                }
            }
        ),
        500: openapi.Response(
            description='Internal server error',
            schema=get_error_response_schema()
        )
    },
    tags=['Authentication']
)


signup_swagger_schema = swagger_auto_schema(
    operation_id='user_signup',
    operation_summary='User Registration',
    operation_description='''
    Register a new user account.
    
    This endpoint:
    - Creates a new user account
    - Automatically logs in the user after registration
    - Returns JWT tokens for immediate use
    - Validates email format and uniqueness
    - Enforces password strength requirements
    - Implements rate limiting (3 registrations per hour)
    ''',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'username', 'nickname', 'password', 'password_confirm'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='email',
                description='Email address (must be unique)',
                example='newuser@example.com'
            ),
            'username': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Username (must be unique, 3+ chars)',
                example='newuser123'
            ),
            'nickname': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Display name (2+ chars)',
                example='New User'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='password',
                description='Password (6+ chars, must contain letter and number)',
                example='password123'
            ),
            'password_confirm': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='password',
                description='Password confirmation',
                example='password123'
            )
        }
    ),
    responses={
        201: openapi.Response(
            description='Account created successfully',
            schema=get_success_response_schema(login_response_data_schema)
        ),
        400: openapi.Response(
            description='Bad request - validation error',
            schema=get_error_response_schema()
        ),
        409: openapi.Response(
            description='Conflict - email or username already exists',
            schema=get_error_response_schema()
        ),
        500: openapi.Response(
            description='Internal server error',
            schema=get_error_response_schema()
        )
    },
    tags=['Authentication']
)


check_email_swagger_schema = swagger_auto_schema(
    operation_id='check_email_availability',
    operation_summary='Check Email Availability',
    operation_description='''
    Check if an email address is available for registration.
    
    This endpoint:
    - Validates email format
    - Checks if email is already registered
    - Returns availability status
    - Fast response for user experience
    ''',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='email',
                description='Email address to check',
                example='check@example.com'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description='Email is available',
            schema=get_success_response_schema(),
            examples={
                'application/json': {
                    'success': True,
                    'status': 'success',
                    'message': 'Email is available',
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345'
                }
            }
        ),
        400: openapi.Response(
            description='Bad request - invalid email format',
            schema=get_error_response_schema()
        ),
        409: openapi.Response(
            description='Conflict - email already exists',
            schema=get_error_response_schema(),
            examples={
                'application/json': {
                    'success': False,
                    'status': 'error',
                    'error': {
                        'code': 'EMAIL_EXISTS',
                        'message': 'User with this email already exists',
                        'status': 409
                    },
                    'timestamp': 1691234567.123,
                    'request_id': 'abc12345'
                }
            }
        )
    },
    tags=['Validation']
)


check_nickname_swagger_schema = swagger_auto_schema(
    operation_id='check_nickname_availability',
    operation_summary='Check Nickname Availability',
    operation_description='''
    Check if a nickname is available.
    
    This endpoint:
    - Validates nickname format
    - Checks if nickname is already taken
    - Returns availability status
    - Fast response for user experience
    ''',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nickname'],
        properties={
            'nickname': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Nickname to check (2+ characters)',
                example='TestUser'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description='Nickname is available',
            schema=get_success_response_schema()
        ),
        400: openapi.Response(
            description='Bad request - invalid nickname',
            schema=get_error_response_schema()
        ),
        409: openapi.Response(
            description='Conflict - nickname already taken',
            schema=get_error_response_schema()
        )
    },
    tags=['Validation']
)


user_me_swagger_schema = swagger_auto_schema(
    operation_id='get_current_user',
    operation_summary='Get Current User',
    operation_description='''
    Get information about the currently authenticated user.
    
    This endpoint:
    - Requires authentication
    - Returns current user profile
    - Fast response with cached data
    ''',
    responses={
        200: openapi.Response(
            description='User data retrieved successfully',
            schema=get_success_response_schema(user_data_schema)
        ),
        401: openapi.Response(
            description='Unauthorized - authentication required',
            schema=get_error_response_schema()
        )
    },
    tags=['User Profile']
)