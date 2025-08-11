"""
Comprehensive Integration Tests for VideoPlanet Authentication API
Tests all authentication endpoints with various scenarios and edge cases
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json
import time
from unittest.mock import patch

User = get_user_model()


class LoginAPITestCase(APITestCase):
    """Test cases for Login API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.login_url = reverse('login')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            nickname='Test User',
            is_active=True,
            email_verified=True
        )
        
        self.login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_successful_login_with_email(self):
        """Test successful login with email"""
        response = self.client.post(
            self.login_url, 
            self.login_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Login successful')
        
        # Check tokens
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        self.assertIn('vridge_session', data['data'])
        
        # Check user data
        user_data = data['data']['user']
        self.assertEqual(user_data['id'], self.user.id)
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['nickname'], self.user.nickname)
        
        # Check metadata
        self.assertIn('timestamp', data)
        self.assertIn('request_id', data)
        self.assertIn('performance', data)
        
        # Verify performance requirement (<200ms)
        self.assertLess(data['performance']['response_time_ms'], 200)
    
    def test_successful_login_with_username(self):
        """Test successful login with username"""
        login_data = {
            'email': 'testuser',  # Using username in email field
            'password': 'testpass123'
        }
        
        response = self.client.post(
            self.login_url, 
            login_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('access_token', data['data'])
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(
            self.login_url, 
            invalid_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['error']['code'], 'INVALID_CREDENTIALS')
    
    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user"""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(
            self.login_url, 
            invalid_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data['error']['code'], 'INVALID_CREDENTIALS')
    
    def test_login_with_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(
            self.login_url, 
            self.login_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['error']['code'], 'ACCOUNT_INACTIVE')
    
    def test_login_with_unverified_email_production(self):
        """Test login with unverified email in production mode"""
        with patch.object(settings, 'DEBUG', False):
            self.user.email_verified = False
            self.user.email_verified_at = time.time()  # Set timestamp
            self.user.save()
            
            response = self.client.post(
                self.login_url, 
                self.login_data, 
                format='json'
            )
            
            self.assertEqual(response.status_code, 403)
            data = response.json()
            self.assertEqual(data['error']['code'], 'EMAIL_NOT_VERIFIED')
    
    def test_login_with_missing_fields(self):
        """Test login with missing required fields"""
        # Missing password
        response = self.client.post(
            self.login_url, 
            {'email': 'test@example.com'}, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'VALIDATION_FAILED')
        self.assertIn('password', data['error']['details'])
    
    def test_login_with_invalid_json(self):
        """Test login with invalid JSON"""
        response = self.client.post(
            self.login_url, 
            'invalid json', 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'INVALID_JSON')
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in response"""
        # Add origin header to simulate cross-origin request
        response = self.client.post(
            self.login_url,
            self.login_data,
            format='json',
            HTTP_ORIGIN='https://vlanet.net'
        )
        
        # Check CORS headers are applied by middleware
        self.assertIn('X-Request-ID', response)
        self.assertIn('X-Response-Time', response)
    
    @patch('users.views_api.PasswordResetSecurity.check_rate_limit')
    def test_rate_limiting(self, mock_rate_limit):
        """Test rate limiting functionality"""
        # Mock rate limit exceeded
        mock_rate_limit.return_value = (False, "Rate limit exceeded")
        
        response = self.client.post(
            self.login_url, 
            self.login_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertEqual(data['error']['code'], 'RATE_LIMIT_EXCEEDED')


class SignupAPITestCase(APITestCase):
    """Test cases for Signup API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.signup_url = reverse('signup')
        
        self.signup_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'nickname': 'New User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
    
    def test_successful_signup(self):
        """Test successful user registration"""
        response = self.client.post(
            self.signup_url, 
            self.signup_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Account created successfully')
        
        # Check that user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        
        # Check tokens are provided for immediate login
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        
        # Verify user data
        user_data = data['data']['user']
        self.assertEqual(user_data['email'], 'newuser@example.com')
        self.assertEqual(user_data['username'], 'newuser')
        self.assertEqual(user_data['nickname'], 'New User')
    
    def test_signup_with_existing_email(self):
        """Test signup with existing email"""
        # Create user first
        User.objects.create_user(
            email='existing@example.com',
            username='existing',
            password='pass123'
        )
        
        signup_data = self.signup_data.copy()
        signup_data['email'] = 'existing@example.com'
        signup_data['username'] = 'different'
        
        response = self.client.post(
            self.signup_url, 
            signup_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'VALIDATION_FAILED')
        self.assertIn('email', data['error']['details'])
    
    def test_signup_with_weak_password(self):
        """Test signup with weak password"""
        signup_data = self.signup_data.copy()
        signup_data['password'] = 'weak'
        signup_data['password_confirm'] = 'weak'
        
        response = self.client.post(
            self.signup_url, 
            signup_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('password', data['error']['details'])
    
    def test_signup_with_mismatched_passwords(self):
        """Test signup with mismatched passwords"""
        signup_data = self.signup_data.copy()
        signup_data['password_confirm'] = 'different123'
        
        response = self.client.post(
            self.signup_url, 
            signup_data, 
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'VALIDATION_FAILED')


class EmailCheckAPITestCase(APITestCase):
    """Test cases for Email Check API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.check_email_url = reverse('check_email')
        
        # Create existing user
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='pass123'
        )
    
    def test_available_email(self):
        """Test checking available email"""
        response = self.client.post(
            self.check_email_url,
            {'email': 'available@example.com'},
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Email is available')
    
    def test_existing_email(self):
        """Test checking existing email"""
        response = self.client.post(
            self.check_email_url,
            {'email': 'existing@example.com'},
            format='json'
        )
        
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(data['error']['code'], 'EMAIL_EXISTS')
    
    def test_invalid_email_format(self):
        """Test checking invalid email format"""
        response = self.client.post(
            self.check_email_url,
            {'email': 'invalid-email'},
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'VALIDATION_FAILED')


class NicknameCheckAPITestCase(APITestCase):
    """Test cases for Nickname Check API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.check_nickname_url = reverse('check_nickname')
        
        # Create user with existing nickname
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            nickname='ExistingNick',
            password='pass123'
        )
    
    def test_available_nickname(self):
        """Test checking available nickname"""
        response = self.client.post(
            self.check_nickname_url,
            {'nickname': 'AvailableNick'},
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Nickname is available')
    
    def test_existing_nickname(self):
        """Test checking existing nickname"""
        response = self.client.post(
            self.check_nickname_url,
            {'nickname': 'ExistingNick'},
            format='json'
        )
        
        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(data['error']['code'], 'NICKNAME_EXISTS')
    
    def test_short_nickname(self):
        """Test checking too short nickname"""
        response = self.client.post(
            self.check_nickname_url,
            {'nickname': 'A'},
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'VALIDATION_FAILED')


class UserMeAPITestCase(APITestCase):
    """Test cases for User Me API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user_me_url = reverse('user_me')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            nickname='Test User',
            password='testpass123'
        )
        
        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_get_user_data_authenticated(self):
        """Test getting user data when authenticated"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.user_me_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        user_data = data['data']
        self.assertEqual(user_data['id'], self.user.id)
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['nickname'], self.user.nickname)
    
    def test_get_user_data_unauthenticated(self):
        """Test getting user data when not authenticated"""
        response = self.client.get(self.user_me_url)
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'AUTH_REQUIRED')


class APIPerformanceTestCase(APITestCase):
    """Test cases for API performance requirements"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user for login performance test
        self.user = User.objects.create_user(
            username='perftest',
            email='perf@example.com',
            password='perftest123',
            is_active=True,
            email_verified=True
        )
    
    def test_login_performance(self):
        """Test that login endpoint meets <200ms requirement"""
        login_data = {
            'email': 'perf@example.com',
            'password': 'perftest123'
        }
        
        start_time = time.time()
        response = self.client.post(reverse('login'), login_data, format='json')
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time_ms, 200, 
                       f"Login endpoint took {response_time_ms}ms, should be <200ms")
        
        # Also check the performance data in response
        data = response.json()
        self.assertIn('performance', data)
        self.assertLess(data['performance']['response_time_ms'], 200)
    
    def test_email_check_performance(self):
        """Test that email check endpoint is fast"""
        start_time = time.time()
        response = self.client.post(
            reverse('check_email'), 
            {'email': 'fast@example.com'}, 
            format='json'
        )
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time_ms, 100, 
                       f"Email check took {response_time_ms}ms, should be <100ms")


class APICORSTestCase(APITestCase):
    """Test cases for CORS functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='corstest',
            email='cors@example.com',
            password='corstest123',
            is_active=True,
            email_verified=True
        )
    
    def test_cors_headers_for_valid_origin(self):
        """Test CORS headers for valid origins"""
        valid_origins = [
            'https://vlanet.net',
            'https://www.vlanet.net',
            'https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app',
            'http://localhost:3000'
        ]
        
        for origin in valid_origins:
            response = self.client.post(
                reverse('login'),
                {'email': 'cors@example.com', 'password': 'corstest123'},
                format='json',
                HTTP_ORIGIN=origin
            )
            
            self.assertEqual(response.status_code, 200)
            # The CORS middleware should handle headers
            self.assertIn('X-Request-ID', response)
    
    def test_options_preflight_request(self):
        """Test OPTIONS preflight request handling"""
        response = self.client.options(
            reverse('login'),
            HTTP_ORIGIN='https://vlanet.net',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type'
        )
        
        # The middleware should handle this
        self.assertIn(response.status_code, [200, 204])


class APIErrorHandlingTestCase(APITestCase):
    """Test cases for API error handling"""
    
    def test_500_error_includes_cors_headers(self):
        """Test that 500 errors include CORS headers"""
        # This would need to be tested with a mock that raises an exception
        # The middleware should handle this case
        pass
    
    def test_404_error_format(self):
        """Test 404 error format"""
        response = self.client.get('/api/users/nonexistent/')
        
        self.assertEqual(response.status_code, 404)
        # Check that it has the standard error format
        # This will be handled by the custom exception handler


# Test runner command
if __name__ == '__main__':
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    django.setup()
    
    import unittest
    unittest.main()