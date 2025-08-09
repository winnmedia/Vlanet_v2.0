'use client';

import React from 'react';
import { Suspense } from 'react';
import { motion } from 'framer-motion';
import { SignupForm } from '@/components/auth/SignupForm';
// import { SocialLoginButtons } from '@/components/auth/SocialLoginButtons';
import { Spinner } from '@/components/ui/Spinner';
import { Logo } from '@/components/ui/Logo';

/**
 * 회원가입 페이지
 */
function SignupPageContent() {
  const handleSignupSuccess = (user: any) => {
    console.log('회원가입 성공:', user);
  };

  const handleSignupError = (error: Error) => {
    console.error('회원가입 오류:', error);
  };

  const _handleSocialSignupSuccess = (provider: 'google' | 'kakao') => {
    console.log(`${provider} 회원가입 성공`);
  };

  const _handleSocialSignupError = (error: Error) => {
    console.error('소셜 회원가입 오류:', error);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="sm:mx-auto sm:w-full sm:max-w-lg"
      >
        {/* 헤더 */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="flex justify-center mb-6"
          >
            <Logo size="lg" variant="default" showText={true} />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-900">회원가입</h2>
          <p className="mt-2 text-gray-600">영상 제작의 새로운 경험을 시작하세요</p>
        </div>

        {/* 회원가입 폼 */}
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
          <SignupForm
            onSuccess={handleSignupSuccess}
            onError={handleSignupError}
            redirectTo="/dashboard"
            showSocialLogin={false} // SignupForm 내부에 소셜 로그인이 포함되어 있음
            className="mb-6"
          />

          {/* 소셜 회원가입 - 임시 비활성화 */}
          <div className="mt-8">
            {/* <SocialLoginButtons
              mode="signup"
              onSuccess={handleSocialSignupSuccess}
              onError={handleSocialSignupError}
            /> */}
          </div>

          {/* 로그인 링크 */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600">
              이미 계정이 있으신가요?{' '}
              <a 
                href="/login" 
                className="font-medium text-brand-primary hover:text-brand-primary-dark transition-colors"
              >
                로그인
              </a>
            </p>
          </div>
        </div>

        {/* 추가 정보 */}
        <div className="mt-6 text-center space-y-4">
          <div className="text-xs text-gray-500 max-w-md mx-auto">
            <p>
              회원가입 시 VideoPlanet의{' '}
              <a href="/terms" target="_blank" rel="noopener noreferrer" className="text-brand-primary hover:underline">
                이용약관
              </a>
              {' '}및{' '}
              <a href="/privacy" target="_blank" rel="noopener noreferrer" className="text-brand-primary hover:underline">
                개인정보처리방침
              </a>
              에 동의하게 됩니다.
            </p>
          </div>
          
          <div>
            <a 
              href="/" 
              className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
            >
              ← 홈으로 돌아가기
            </a>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    }>
      <SignupPageContent />
    </Suspense>
  );
}