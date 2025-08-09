'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface EmailVerificationFormProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  initialEmail?: string;
  tokenType?: 'email_verification' | 'password_reset' | 'account_recovery';
}

export function EmailVerificationForm({ 
  onSuccess, 
  onError, 
  initialEmail = '', 
  tokenType = 'email_verification' 
}: EmailVerificationFormProps) {
  const [step, setStep] = useState<'email' | 'code'>('email');
  const [email, setEmail] = useState(initialEmail);
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);

  // 인증 이메일 요청
  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/account/verify-email/request/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email.trim(),
          token_type: tokenType 
        }),
      });

      const data = await response.json();

      if (data.success) {
        setStep('code');
        startResendCooldown();
      } else {
        setError(data.message || '인증 이메일 발송에 실패했습니다.');
        onError?.(new Error(data.message));
      }
    } catch (err) {
      const error = err as Error;
      setError('네트워크 오류가 발생했습니다.');
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  // 인증 코드 확인
  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/account/verify-email/confirm/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email.trim(), 
          verification_code: verificationCode.trim(),
          token_type: tokenType 
        }),
      });

      const data = await response.json();

      if (data.success) {
        onSuccess?.();
      } else {
        setError(data.message || '인증에 실패했습니다.');
        onError?.(new Error(data.message));
      }
    } catch (err) {
      const error = err as Error;
      setError('네트워크 오류가 발생했습니다.');
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  // 재발송 쿨다운 관리
  const startResendCooldown = () => {
    setResendCooldown(60);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // 인증 코드 재발송
  const handleResendCode = async () => {
    if (resendCooldown > 0) return;
    
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/account/verify-email/request/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email.trim(),
          token_type: tokenType 
        }),
      });

      const data = await response.json();

      if (data.success) {
        startResendCooldown();
        alert('인증 코드가 재발송되었습니다.');
      } else {
        setError(data.message || '재발송에 실패했습니다.');
      }
    } catch (err) {
      setError('네트워크 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <AnimatePresence mode="wait">
        {step === 'email' ? (
          <motion.form
            key="email-form"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            onSubmit={handleSendCode}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                이메일 주소
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="example@email.com"
                required
                disabled={isLoading}
                className="w-full"
              />
              <p className="mt-1 text-xs text-gray-500">
                가입 시 사용한 이메일 주소를 입력해주세요.
              </p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border border-red-200 rounded-lg p-3"
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-red-800">{error}</span>
                </div>
              </motion.div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={isLoading || !email.trim()}
            >
              {isLoading ? '발송 중...' : '인증 코드 발송'}
            </Button>
          </motion.form>
        ) : (
          <motion.form
            key="code-form"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            onSubmit={handleVerifyCode}
            className="space-y-4"
          >
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="font-medium text-green-800">인증 코드를 발송했습니다!</span>
              </div>
              <p className="text-sm text-green-700">
                <span className="font-medium">{email}</span>로 발송된 6자리 인증 코드를 입력해주세요.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                인증 코드
              </label>
              <Input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                placeholder="123456"
                required
                disabled={isLoading}
                className="w-full text-center text-xl font-mono tracking-widest"
                maxLength={6}
              />
              <p className="mt-1 text-xs text-gray-500">
                인증 코드는 10분간 유효합니다.
              </p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border border-red-200 rounded-lg p-3"
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-red-800">{error}</span>
                </div>
              </motion.div>
            )}

            <div className="flex gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setStep('email');
                  setVerificationCode('');
                  setError('');
                }}
                disabled={isLoading}
                className="flex-1"
              >
                이메일 변경
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                disabled={isLoading || verificationCode.length !== 6}
              >
                {isLoading ? '인증 중...' : '인증 확인'}
              </Button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={handleResendCode}
                disabled={resendCooldown > 0 || isLoading}
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors disabled:text-gray-400"
              >
                {resendCooldown > 0 
                  ? `재발송까지 ${resendCooldown}초` 
                  : '인증 코드 재발송'
                }
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}