'use client';

import React from 'react';
import { Suspense } from 'react';
import { motion } from 'framer-motion';
import { PasswordResetForm } from '@/components/auth/PasswordResetForm';
import { Spinner } from '@/components/ui/Spinner';

/**
 * 비밀번호 재설정 페이지
 */
function ResetPasswordPageContent() {
  const handleResetSuccess = () => {
    console.log('비밀번호 재설정 성공');
  };

  const handleResetError = (error: Error) => {
    console.error('비밀번호 재설정 오류:', error);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="sm:mx-auto sm:w-full sm:max-w-md"
      >
        {/* 헤더 */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mx-auto h-12 w-12 bg-brand-primary rounded-lg flex items-center justify-center mb-6"
          >
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-900">VideoPlanet</h2>
          <p className="mt-2 text-gray-600">안전한 비밀번호 재설정</p>
        </div>

        {/* 비밀번호 재설정 폼 */}
        <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
          <PasswordResetForm
            onSuccess={handleResetSuccess}
            onError={handleResetError}
          />
        </div>

        {/* 도움말 */}
        <div className="mt-6 text-center space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">도움말</span>
            </div>
            <ul className="text-left space-y-1 text-xs">
              <li>• 가입 시 사용한 이메일 주소를 정확히 입력해주세요</li>
              <li>• 재설정 링크는 10분간 유효합니다</li>
              <li>• 이메일이 오지 않는다면 스팸함을 확인해보세요</li>
              <li>• 문제가 계속되면 고객센터에 문의해주세요</li>
            </ul>
          </div>

          <div className="space-y-2">
            <div>
              <a 
                href="/login" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                로그인 페이지로 돌아가기
              </a>
            </div>
            <div>
              <a 
                href="/signup" 
                className="text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                계정이 없다면 회원가입
              </a>
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
        </div>
      </motion.div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    }>
      <ResetPasswordPageContent />
    </Suspense>
  );
}