'use client';

import React from 'react';
import { Suspense } from 'react';
import { motion } from 'framer-motion';
import { SignupForm } from '@/components/auth/SignupForm';
// import { SocialLoginButtons } from '@/components/auth/SocialLoginButtons';
import { Spinner } from '@/components/ui/Spinner';
import { Logo } from '@/components/ui/Logo';

/**
 *  
 */
function SignupPageContent() {
  const handleSignupSuccess = (user: any) => {
    console.log(' :', user);
  };

  const handleSignupError = (error: Error) => {
    console.error(' :', error);
  };

  const _handleSocialSignupSuccess = (provider: 'google' | 'kakao') => {
    console.log(`${provider}  `);
  };

  const _handleSocialSignupError = (error: Error) => {
    console.error('  :', error);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="sm:mx-auto sm:w-full sm:max-w-lg"
      >
        {/*  */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="flex justify-center mb-6"
          >
            <Logo size="lg" variant="default" showText={true} />
          </motion.div>
          <h2 className="text-2xl font-bold text-gray-900">VideoPlanet에 오신 것을 환영합니다</h2>
          <p className="mt-2 text-gray-600">계정을 생성하여 영상 기획 여정을 시작하세요</p>
        </div>

        {/*   */}
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
          <SignupForm
            onSuccess={handleSignupSuccess}
            onError={handleSignupError}
            redirectTo="/dashboard"
            showSocialLogin={false} // SignupForm     
            className="mb-6"
          />

          {/*   -   */}
          <div className="mt-8">
            {/* <SocialLoginButtons
              mode="signup"
              onSuccess={handleSocialSignupSuccess}
              onError={handleSocialSignupError}
            /> */}
          </div>

          {/* 로그인 링크는 SignupForm 컴포넌트에서 처리하므로 여기서는 제거 */}
        </div>

        {/*   */}
        <div className="mt-6 text-center space-y-4">
          <div className="text-xs text-gray-500 max-w-md mx-auto">
            <p>
              회원가입을 진행하면 VideoPlanet의{' '}
              <a href="/terms" target="_blank" rel="noopener noreferrer" className="text-brand-primary hover:underline">
                이용약관
              </a>
              {' '}및{' '}
              <a href="/privacy" target="_blank" rel="noopener noreferrer" className="text-brand-primary hover:underline">
                개인정보처리방침
              </a>
              에 동의한 것으로 간주됩니다.
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