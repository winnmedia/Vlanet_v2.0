# -*- coding: utf-8 -*-
"""
계정 관리 서비스 모듈
- 이메일 인증
- ID/PW 찾기
- 계정 삭제/복구
"""
import logging
import random
import string
import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from . import models
from .validators import InputValidator

logger = logging.getLogger(__name__)


class AccountManagementService:
    """계정 관리 통합 서비스"""

    @staticmethod
    def generate_verification_code(length=6):
        """인증 코드 생성"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def generate_temp_password(length=12):
        """임시 비밀번호 생성"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def send_email(subject, body, to_email, html_message=None):
        """이메일 발송 공통 함수"""
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            if html_message:
                email.attach_alternative(html_message, "text/html")
            
            result = email.send()
            logger.info(f"이메일 발송 성공: {to_email}")
            return result > 0
        except Exception as e:
            logger.error(f"이메일 발송 실패 ({to_email}): {str(e)}")
            return False


class EmailVerificationService(AccountManagementService):
    """이메일 인증 서비스"""

    @classmethod
    def send_verification_email(cls, user_email, token_type='email_verification'):
        """인증 이메일 발송"""
        try:
            # 기존 미인증 토큰 삭제
            models.EmailVerificationToken.objects.filter(
                email=user_email,
                token_type=token_type,
                is_verified=False
            ).delete()

            # 새 토큰 생성
            verification_code = cls.generate_verification_code()
            token = models.EmailVerificationToken.objects.create(
                email=user_email,
                token_type=token_type,
                verification_code=verification_code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )

            # 이메일 템플릿
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet 이메일 인증</title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">이메일 인증</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px; text-align: center;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            다음 인증 코드를 입력해주세요:
                        </p>
                        
                        <div style="background: #1631F8; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px;">{verification_code}</span>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">
                            이 인증 코드는 10분간 유효합니다.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            success = cls.send_email(
                subject="VideoPlanet 이메일 인증",
                body=strip_tags(html_message),
                to_email=user_email,
                html_message=html_message
            )

            return (token, "인증 이메일이 발송되었습니다.") if success else (None, "이메일 발송에 실패했습니다.")

        except Exception as e:
            logger.error(f"인증 이메일 발송 오류: {str(e)}")
            return None, "인증 이메일 발송 중 오류가 발생했습니다."

    @classmethod
    def verify_email_code(cls, email, verification_code, token_type='email_verification'):
        """이메일 인증 코드 검증"""
        try:
            token = models.EmailVerificationToken.objects.filter(
                email=email,
                token_type=token_type,
                verification_code=verification_code,
                is_verified=False
            ).first()

            if not token:
                return False, "인증 코드가 잘못되었습니다."

            if token.is_expired():
                return False, "인증 코드가 만료되었습니다."

            if token.is_max_attempts_reached():
                return False, "최대 시도 횟수를 초과했습니다."

            # 인증 성공
            token.is_verified = True
            token.verified_at = timezone.now()
            token.save()

            return True, "이메일 인증이 완료되었습니다."

        except Exception as e:
            logger.error(f"이메일 인증 검증 오류: {str(e)}")
            return False, "인증 처리 중 오류가 발생했습니다."


class AccountRecoveryService(AccountManagementService):
    """ID/PW 찾기 서비스"""

    @classmethod
    def find_username_by_email(cls, email):
        """이메일로 사용자명 찾기"""
        try:
            # 이메일 유효성 검증
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return False, error_msg

            # 사용자 찾기 (삭제된 계정 제외)
            user = models.User.objects.filter(
                email=email,
                is_deleted=False,
                login_method='email'
            ).first()

            if not user:
                return False, "해당 이메일로 가입된 계정을 찾을 수 없습니다."

            # ID 찾기 이메일 발송
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet ID 찾기</title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">ID 찾기</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            요청하신 계정 정보입니다:
                        </p>
                        
                        <div style="background: #1631F8; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-size: 16px;">아이디(이메일)</p>
                            <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold;">{user.username}</p>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">
                            가입일: {user.date_joined.strftime('%Y년 %m월 %d일')}
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            success = cls.send_email(
                subject="VideoPlanet ID 찾기 결과",
                body=strip_tags(html_message),
                to_email=email,
                html_message=html_message
            )

            return success, "계정 정보가 이메일로 발송되었습니다." if success else "이메일 발송에 실패했습니다."

        except Exception as e:
            logger.error(f"ID 찾기 오류: {str(e)}")
            return False, "ID 찾기 중 오류가 발생했습니다."

    @classmethod
    def send_password_reset_email(cls, email):
        """비밀번호 재설정 이메일 발송"""
        try:
            # 이메일 유효성 검증
            is_valid, error_msg = InputValidator.validate_email(email)
            if not is_valid:
                return False, error_msg

            # 사용자 찾기 (삭제된 계정 제외)
            user = models.User.objects.filter(
                email=email,
                is_deleted=False,
                login_method='email'
            ).first()

            if not user:
                return False, "해당 이메일로 가입된 계정을 찾을 수 없습니다."

            # 인증 토큰 생성
            token, message = EmailVerificationService.send_verification_email(
                email, 'password_reset'
            )

            if not token:
                return False, message

            return True, "비밀번호 재설정 인증 이메일이 발송되었습니다."

        except Exception as e:
            logger.error(f"비밀번호 재설정 이메일 발송 오류: {str(e)}")
            return False, "비밀번호 재설정 중 오류가 발생했습니다."

    @classmethod
    def reset_password_with_code(cls, email, verification_code, new_password):
        """인증 코드로 비밀번호 재설정"""
        try:
            # 인증 코드 검증
            is_verified, message = EmailVerificationService.verify_email_code(
                email, verification_code, 'password_reset'
            )

            if not is_verified:
                return False, message

            # 사용자 찾기
            user = models.User.objects.filter(
                email=email,
                is_deleted=False,
                login_method='email'
            ).first()

            if not user:
                return False, "사용자를 찾을 수 없습니다."

            # 비밀번호 유효성 검증
            is_valid, error_msg = InputValidator.validate_password(new_password)
            if not is_valid:
                return False, error_msg

            # 비밀번호 변경
            user.set_password(new_password)
            user.save()

            logger.info(f"비밀번호 재설정 완료: {user.email}")
            return True, "비밀번호가 성공적으로 변경되었습니다."

        except Exception as e:
            logger.error(f"비밀번호 재설정 오류: {str(e)}")
            return False, "비밀번호 재설정 중 오류가 발생했습니다."


class AccountDeletionService(AccountManagementService):
    """계정 삭제/복구 서비스"""

    @classmethod
    def soft_delete_account(cls, user, reason="사용자 요청"):
        """계정 소프트 삭제"""
        try:
            # 이미 삭제된 계정인지 확인
            if user.is_deleted:
                return False, "이미 삭제된 계정입니다."

            # 계정 소프트 삭제
            user.soft_delete(reason)

            # 삭제 알림 이메일 발송
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet 계정 삭제</title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">계정 삭제 안내</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            안녕하세요, {user.nickname or user.username}님.
                        </p>
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            요청하신 대로 계정이 삭제되었습니다.
                        </p>
                        
                        <div style="border: 2px solid #ff6b6b; padding: 20px; border-radius: 8px; margin: 20px 0; background: #ffe0e0;">
                            <p style="margin: 0; font-size: 14px; color: #d63031;">
                                <strong>중요:</strong> 계정은 30일 동안 복구 가능합니다.
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 14px; color: #d63031;">
                                복구 마감일: {user.recovery_deadline.strftime('%Y년 %m월 %d일')}
                            </p>
                        </div>
                        
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">
                            계정을 복구하려면 고객센터로 문의해 주세요.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            cls.send_email(
                subject="VideoPlanet 계정 삭제 완료",
                body=strip_tags(html_message),
                to_email=user.email,
                html_message=html_message
            )

            logger.info(f"계정 소프트 삭제 완료: {user.email}")
            return True, "계정이 삭제되었습니다. 30일 내에 복구 가능합니다."

        except Exception as e:
            logger.error(f"계정 삭제 오류: {str(e)}")
            return False, "계정 삭제 중 오류가 발생했습니다."

    @classmethod
    def restore_account(cls, email):
        """계정 복구"""
        try:
            # 삭제된 계정 찾기
            user = models.User.objects.filter(
                email=email,
                is_deleted=True
            ).first()

            if not user:
                return False, "삭제된 계정을 찾을 수 없습니다."

            if not user.can_be_recovered():
                return False, "복구 기간이 만료되었거나 복구할 수 없는 계정입니다."

            # 계정 복구
            user.restore_account()

            # 복구 알림 이메일 발송
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>VideoPlanet 계정 복구</title>
            </head>
            <body style="font-family: Arial, sans-serif; padding: 20px; margin: 0; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 10px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #1631F8; margin: 0; font-size: 32px;">VideoPlanet</h1>
                        <p style="color: #666; margin-top: 10px; font-size: 18px;">계정 복구 완료</p>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 30px; border-radius: 8px;">
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            안녕하세요, {user.nickname or user.username}님.
                        </p>
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            계정이 성공적으로 복구되었습니다.
                        </p>
                        
                        <div style="background: #00b894; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-size: 18px; font-weight: bold; text-align: center;">
                                이제 다시 로그인하실 수 있습니다!
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            cls.send_email(
                subject="VideoPlanet 계정 복구 완료",
                body=strip_tags(html_message),
                to_email=user.email,
                html_message=html_message
            )

            logger.info(f"계정 복구 완료: {user.email}")
            return True, "계정이 성공적으로 복구되었습니다."

        except Exception as e:
            logger.error(f"계정 복구 오류: {str(e)}")
            return False, "계정 복구 중 오류가 발생했습니다."