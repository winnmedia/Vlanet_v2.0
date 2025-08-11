"""
Enhanced API Serializers for User Authentication
Provides comprehensive validation, error handling, and standardized responses
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import User
import re
import logging

logger = logging.getLogger(__name__)


class LoginRequestSerializer(serializers.Serializer):
    """
    Login request validation serializer
    Supports both email and username login
    """
    email = serializers.CharField(
        required=True,
        max_length=254,
        help_text="Email address or username for login"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password"
    )
    
    def validate_email(self, value):
        """Validate email format if it looks like an email"""
        if not value:
            raise serializers.ValidationError("Email or username is required")
        
        # Check if it looks like an email
        if '@' in value:
            email_validator = EmailValidator()
            try:
                email_validator(value)
            except ValidationError:
                raise serializers.ValidationError("Invalid email format")
        
        # Check length
        if len(value) > 254:
            raise serializers.ValidationError("Email/username too long")
        
        return value.lower().strip()
    
    def validate_password(self, value):
        """Basic password validation"""
        if not value:
            raise serializers.ValidationError("Password is required")
        
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        
        return value
    
    def validate(self, attrs):
        """Perform authentication validation"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required")
        
        return attrs


class UserDataSerializer(serializers.ModelSerializer):
    """User data serializer for login response"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname', 
            'login_method', 'email_verified', 'is_active',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def to_representation(self, instance):
        """Customize the output representation"""
        data = super().to_representation(instance)
        
        # Ensure nickname has a fallback
        if not data.get('nickname'):
            data['nickname'] = instance.username or instance.email.split('@')[0] if instance.email else 'User'
        
        # Format dates
        if data.get('date_joined'):
            data['date_joined'] = instance.date_joined.isoformat() if instance.date_joined else None
        if data.get('last_login'):
            data['last_login'] = instance.last_login.isoformat() if instance.last_login else None
        
        return data


class LoginResponseSerializer(serializers.Serializer):
    """Login response serializer"""
    access_token = serializers.CharField(help_text="JWT access token")
    refresh_token = serializers.CharField(help_text="JWT refresh token") 
    vridge_session = serializers.CharField(help_text="Session token for compatibility")
    user = UserDataSerializer(help_text="User data")
    expires_in = serializers.IntegerField(help_text="Token expiry time in seconds")
    
    # Legacy compatibility fields
    access = serializers.CharField(help_text="Legacy access token field")
    refresh = serializers.CharField(help_text="Legacy refresh token field")


class SignupRequestSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password (min 6 characters)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm password"
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'nickname', 'password', 'password_confirm']
    
    def validate_email(self, value):
        """Email validation"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        
        return value.lower().strip()
    
    def validate_username(self, value):
        """Username validation"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists")
        
        # Username format validation
        if not re.match(r'^[a-zA-Z0-9._-]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, dots, dashes and underscores")
        
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        
        return value.lower().strip()
    
    def validate_nickname(self, value):
        """Nickname validation"""
        if len(value) < 2:
            raise serializers.ValidationError("Nickname must be at least 2 characters long")
        
        return value.strip()
    
    def validate_password(self, value):
        """Password strength validation"""
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        
        # Check for at least one letter and one number
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one letter and one number")
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError("Passwords do not match")
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        logger.info(f"New user created: {user.email}")
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Password reset request serializer"""
    email = serializers.EmailField(
        required=True,
        help_text="Email address to send password reset link"
    )
    
    def validate_email(self, value):
        """Validate that user exists"""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal whether user exists for security
            pass
        
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer"""
    token = serializers.CharField(
        required=True,
        help_text="Password reset token"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password"
    )
    
    def validate_new_password(self, value):
        """Password strength validation"""
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one letter and one number")
        
        return value


class EmailValidationSerializer(serializers.Serializer):
    """Email validation serializer"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        return value.lower().strip()


class NicknameValidationSerializer(serializers.Serializer):
    """Nickname validation serializer"""
    nickname = serializers.CharField(required=True, max_length=100)
    
    def validate_nickname(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Nickname must be at least 2 characters long")
        return value.strip()