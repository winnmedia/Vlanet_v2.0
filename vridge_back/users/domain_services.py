"""
Domain Services for User Management
Following DDD principles with clear boundaries and responsibilities
"""

from typing import Dict, Optional, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging

from .models import User, UserProfile, EmailVerify, EmailVerificationToken

logger = logging.getLogger(__name__)


class EmailVerificationDomainService:
    """
    도메인 서비스: 이메일 인증 관련 비즈니스 로직
    """
    
    VERIFICATION_CODE_LENGTH = 6
    VERIFICATION_EXPIRY_MINUTES = 10
    MAX_VERIFICATION_ATTEMPTS = 5
    
    @classmethod
    def generate_verification_code(cls) -> str:
        """6자리 인증 코드 생성"""
        return ''.join(random.choices(string.digits, k=cls.VERIFICATION_CODE_LENGTH))
    
    @classmethod
    @transaction.atomic
    def create_verification_request(cls, email: str) -> Tuple[bool, Dict]:
        """
        이메일 인증 요청 생성
        
        Returns:
            Tuple[성공여부, 결과 데이터]
        """
        try:
            # 기존 미인증 요청 삭제
            EmailVerify.objects.filter(
                email=email,
                is_verified=False
            ).delete()
            
            # 새 인증 코드 생성
            auth_code = cls.generate_verification_code()
            expires_at = timezone.now() + timedelta(minutes=cls.VERIFICATION_EXPIRY_MINUTES)
            
            # 인증 요청 저장
            verification = EmailVerify.objects.create(
                email=email,
                auth_number=auth_code,
                expires_at=expires_at
            )
            
            logger.info(f"Verification code created for {email}: {auth_code}")
            
            return True, {
                'email': email,
                'auth_code': auth_code,  # 실제 운영환경에서는 이메일로만 발송
                'expires_at': expires_at,
                'expires_in_seconds': cls.VERIFICATION_EXPIRY_MINUTES * 60
            }
            
        except Exception as e:
            logger.error(f"Failed to create verification request: {e}")
            return False, {'error': str(e)}
    
    @classmethod
    @transaction.atomic
    def verify_code(cls, email: str, code: str) -> Tuple[bool, str]:
        """
        인증 코드 검증
        
        Returns:
            Tuple[성공여부, 메시지]
        """
        try:
            verification = EmailVerify.objects.filter(
                email=email,
                auth_number=code,
                is_verified=False
            ).first()
            
            if not verification:
                return False, "잘못된 인증 코드입니다."
            
            # 만료 시간 체크
            if verification.expires_at and timezone.now() > verification.expires_at:
                verification.delete()
                return False, "인증 코드가 만료되었습니다."
            
            # 인증 완료 처리
            verification.is_verified = True
            verification.verified_at = timezone.now()
            verification.save()
            
            return True, "이메일 인증이 완료되었습니다."
            
        except Exception as e:
            logger.error(f"Failed to verify code: {e}")
            return False, "인증 처리 중 오류가 발생했습니다."


class UserRegistrationDomainService:
    """
    도메인 서비스: 사용자 등록 관련 비즈니스 로직
    """
    
    @classmethod
    @transaction.atomic
    def check_email_availability(cls, email: str) -> Dict:
        """
        이메일 사용 가능 여부 확인
        
        Returns:
            Dict with availability status and verification info
        """
        try:
            # 이메일 중복 체크
            user_exists = User.objects.filter(email=email).exists()
            
            # 인증 상태 체크
            verification = EmailVerify.objects.filter(
                email=email,
                is_verified=True
            ).order_by('-verified_at').first()
            
            is_verified = verification is not None
            
            return {
                'email': email,
                'available': not user_exists,
                'verified': is_verified,
                'message': cls._get_availability_message(user_exists, is_verified)
            }
            
        except Exception as e:
            logger.error(f"Failed to check email availability: {e}")
            raise
    
    @classmethod
    def _get_availability_message(cls, exists: bool, verified: bool) -> str:
        """가용성 메시지 생성"""
        if exists:
            return "이미 등록된 이메일입니다."
        elif not verified:
            return "사용 가능한 이메일입니다. 인증이 필요합니다."
        else:
            return "사용 가능하며 인증된 이메일입니다."
    
    @classmethod
    @transaction.atomic
    def check_nickname_availability(cls, nickname: str) -> Dict:
        """
        닉네임 사용 가능 여부 확인
        """
        try:
            exists = User.objects.filter(nickname=nickname).exists()
            
            return {
                'nickname': nickname,
                'available': not exists,
                'message': "이미 사용중인 닉네임입니다." if exists else "사용 가능한 닉네임입니다."
            }
            
        except Exception as e:
            logger.error(f"Failed to check nickname availability: {e}")
            raise
    
    @classmethod
    @transaction.atomic
    def register_user(cls, validated_data: Dict) -> Tuple[Optional[User], Optional[str]]:
        """
        사용자 등록 (User + UserProfile 생성)
        
        Args:
            validated_data: 검증된 회원가입 데이터
            
        Returns:
            Tuple[User 객체 또는 None, 에러 메시지 또는 None]
        """
        try:
            # 이메일 인증 확인
            email = validated_data.get('email')
            verification = EmailVerify.objects.filter(
                email=email,
                is_verified=True
            ).first()
            
            if not verification:
                return None, "이메일 인증이 필요합니다."
            
            # User 생성
            user_data = {
                'username': email,  # username으로 email 사용
                'email': email,
                'nickname': validated_data.get('nickname'),
                'full_name': validated_data.get('full_name', ''),
                'login_method': 'email',
                'email_verified': True,
                'email_verified_at': timezone.now()
            }
            
            password = validated_data.pop('password', None)
            user = User(**user_data)
            
            if password:
                user.set_password(password)
            
            user.save()
            
            # UserProfile 생성
            profile_data = {
                'phone': validated_data.get('phone', ''),
                'company': validated_data.get('company', ''),
                'position': validated_data.get('position', ''),
                'bio': validated_data.get('bio', '')
            }
            
            UserProfile.objects.create(user=user, **profile_data)
            
            # 인증 기록 정리
            EmailVerify.objects.filter(email=email).delete()
            
            logger.info(f"User registered successfully: {email}")
            return user, None
            
        except Exception as e:
            logger.error(f"Failed to register user: {e}")
            return None, f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"


class UserDuplicationCheckService:
    """
    통합 중복 체크 서비스
    이메일 인증과 중복 체크를 동시에 처리
    """
    
    @classmethod
    def check_and_send_verification(cls, email: str) -> Dict:
        """
        이메일 중복 체크 + 인증 코드 발송
        
        Returns:
            Dict with status and action required
        """
        try:
            # 1. 이메일 중복 체크
            availability = UserRegistrationDomainService.check_email_availability(email)
            
            if not availability['available']:
                return {
                    'success': False,
                    'available': False,
                    'message': availability['message'],
                    'action': 'none'
                }
            
            # 2. 이미 인증된 경우
            if availability['verified']:
                return {
                    'success': True,
                    'available': True,
                    'verified': True,
                    'message': "사용 가능하며 인증된 이메일입니다.",
                    'action': 'proceed'
                }
            
            # 3. 인증 코드 발송
            success, result = EmailVerificationDomainService.create_verification_request(email)
            
            if success:
                # 실제로는 이메일 발송 서비스 호출
                from .email_verification_service import EmailVerificationService
                EmailVerificationService.send_verification_code_email(email, result['auth_code'])
                
                return {
                    'success': True,
                    'available': True,
                    'verified': False,
                    'message': "인증 코드가 이메일로 발송되었습니다.",
                    'action': 'verify',
                    'expires_in': result['expires_in_seconds']
                }
            else:
                return {
                    'success': False,
                    'message': "인증 코드 발송에 실패했습니다.",
                    'action': 'retry'
                }
                
        except Exception as e:
            logger.error(f"Failed in check_and_send_verification: {e}")
            return {
                'success': False,
                'message': "처리 중 오류가 발생했습니다.",
                'action': 'error'
            }