'use client';

import React, { useState, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FindAccountForm } from '@/components/auth/FindAccountForm';
import { Spinner } from '@/components/ui/Spinner';

type TabType = 'username' | 'password';

/**
 * 계정/비밀번호 찾기 페이지
 */
function FindAccountPageContent() {
  const [activeTab, setActiveTab] = useState<TabType>('username');
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSuccess = () => {
    setShowSuccess(true);
    if (activeTab === 'username') {
      // 아이디 찾기 성공 시 
      setTimeout(() => {
        window.location.href = '/login';
      }, 3000);
    }
  };

  const handleError = (error: Error) => {
    console.error('계정 찾기 오류:', error);
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </motion.div>
          <h2 className="text-3xl font-bold text-gray-900">VideoPlanet</h2>
          <p className="mt-2 text-gray-600">계정 정보 찾기</p>
        </div>

        {showSuccess && activeTab === 'username' ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10"
          >
            <div className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900">이메일을 발송했습니다</h3>
              <p className="text-gray-600">
                가입하신 이메일로 계정 정보를 발송했습니다.<br />
                이메일을 확인해주세요.
              </p>
              <p className="text-sm text-gray-500">3초 후 로그인 페이지로 이동합니다...</p>
            </div>
          </motion.div>
        ) : (
          <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10">
            {/* 탭 메뉴 */}
            <div className="flex mb-8">
              <button
                onClick={() => setActiveTab('username')}
                className={`flex-1 py-3 text-center text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'username'
                    ? 'border-brand-primary text-brand-primary'
                    : 'border-gray-200 text-gray-500 hover:text-gray-700'
                }`}
              >
                아이디 찾기
              </button>
              <button
                onClick={() => setActiveTab('password')}
                className={`flex-1 py-3 text-center text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'password'
                    ? 'border-brand-primary text-brand-primary'
                    : 'border-gray-200 text-gray-500 hover:text-gray-700'
                }`}
              >
                비밀번호 재설정
              </button>
            </div>

            {/* 폼 컨텐츠 */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <FindAccountForm
                  type={activeTab}
                  onSuccess={handleSuccess}
                  onError={handleError}
                />
              </motion.div>
            </AnimatePresence>
          </div>
        )}

        {/* 도움말 및 링크 */}
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
              <li>• 소셜 로그인으로 가입한 경우 해당 플랫폼을 이용해주세요</li>
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

export default function FindAccountPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    }>
      <FindAccountPageContent />
    </Suspense>
  );
}