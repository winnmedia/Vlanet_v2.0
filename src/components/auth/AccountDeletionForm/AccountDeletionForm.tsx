'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface AccountDeletionFormProps {
  onSuccess?: (recoveryDeadline?: string) => void;
  onError?: (error: Error) => void;
  onCancel?: () => void;
}

export function AccountDeletionForm({ onSuccess, onError, onCancel }: AccountDeletionFormProps) {
  const [step, setStep] = useState<'warning' | 'confirmation' | 'password'>('warning');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [deletionReason, setDeletionReason] = useState('');
  const [confirmationText, setConfirmationText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [agreedToDelete, setAgreedToDelete] = useState(false);

  const CONFIRMATION_TEXT = '계정을 삭제하겠습니다';

  // 계정 삭제 실행
  const handleDeleteAccount = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/account/delete/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`,
        },
        body: JSON.stringify({ 
          confirm_password: confirmPassword,
          reason: deletionReason || '사용자 요청'
        }),
      });

      const data = await response.json();

      if (data.success) {
        // 로컬 스토리지 정리
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        onSuccess?.(data.recovery_deadline);
      } else {
        setError(data.message || '계정 삭제에 실패했습니다.');
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

  // 다음 단계로 진행
  const handleNextStep = () => {
    if (step === 'warning') {
      setStep('confirmation');
    } else if (step === 'confirmation') {
      setStep('password');
    }
  };

  const canProceedFromWarning = agreedToDelete;
  const canProceedFromConfirmation = confirmationText === CONFIRMATION_TEXT;
  const canDeleteAccount = confirmPassword.length > 0;

  return (
    <div className="space-y-6">
      {step === 'warning' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* 경고 메시지 */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-red-500 mt-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <h3 className="font-bold text-red-800 mb-2">계정 삭제 전 반드시 확인해주세요</h3>
                <ul className="space-y-2 text-sm text-red-700">
                  <li>• 모든 프로젝트와 데이터가 삭제됩니다</li>
                  <li>• 친구 관계와 채팅 기록이 사라집니다</li>
                  <li>• 업로드한 모든 파일이 삭제됩니다</li>
                  <li>• 구매 기록과 포인트가 모두 사라집니다</li>
                </ul>
              </div>
            </div>
          </div>

          {/* 복구 안내 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-medium text-blue-800 mb-1">계정 복구 안내</p>
                <p className="text-sm text-blue-700">
                  계정 삭제 후 <span className="font-bold">30일 내</span>에 고객센터에 문의하시면 계정을 복구할 수 있습니다.
                </p>
              </div>
            </div>
          </div>

          {/* 삭제 사유 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              삭제 사유 (선택)
            </label>
            <textarea
              value={deletionReason}
              onChange={(e) => setDeletionReason(e.target.value)}
              placeholder="계정을 삭제하는 이유를 알려주세요. (서비스 개선에 활용됩니다)"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent"
              maxLength={200}
            />
            <p className="mt-1 text-xs text-gray-500">{deletionReason.length}/200</p>
          </div>

          {/* 동의 체크박스 */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="agree-delete"
              checked={agreedToDelete}
              onChange={(e) => setAgreedToDelete(e.target.checked)}
              className="mt-1 w-4 h-4 text-brand-primary border-gray-300 rounded focus:ring-brand-primary"
            />
            <label htmlFor="agree-delete" className="text-sm text-gray-700">
              위 내용을 모두 확인했으며, 계정 삭제에 동의합니다. 
              삭제된 데이터는 복구할 수 없음을 이해했습니다.
            </label>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={onCancel}
              className="flex-1"
            >
              취소
            </Button>
            <Button
              type="button"
              variant="danger"
              onClick={handleNextStep}
              disabled={!canProceedFromWarning}
              className="flex-1"
            >
              계속하기
            </Button>
          </div>
        </motion.div>
      )}

      {step === 'confirmation' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">정말로 계정을 삭제하시겠습니까?</h3>
            <p className="text-gray-600">
              이 작업은 되돌릴 수 없으며, 모든 데이터가 영구적으로 삭제됩니다.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              계속하려면 다음 문구를 정확히 입력하세요:
            </label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-2">
              <code className="text-sm font-mono">{CONFIRMATION_TEXT}</code>
            </div>
            <Input
              type="text"
              value={confirmationText}
              onChange={(e) => setConfirmationText(e.target.value)}
              placeholder="위 문구를 입력하세요"
              className="w-full"
              autoComplete="off"
            />
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setStep('warning')}
              className="flex-1"
            >
              이전
            </Button>
            <Button
              type="button"
              variant="danger"
              onClick={handleNextStep}
              disabled={!canProceedFromConfirmation}
              className="flex-1"
            >
              다음
            </Button>
          </div>
        </motion.div>
      )}

      {step === 'password' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">마지막 확인</h3>
            <p className="text-gray-600">
              계정 삭제를 위해 현재 비밀번호를 입력해주세요.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              현재 비밀번호
            </label>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="현재 비밀번호를 입력하세요"
              required
              disabled={isLoading}
              className="w-full"
            />
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

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div className="text-sm text-red-700">
                <p className="font-medium mb-1">최종 경고</p>
                <p>계정 삭제 버튼을 클릭하면 즉시 계정이 삭제되며, 30일 후에는 완전히 복구할 수 없습니다.</p>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setStep('confirmation')}
              disabled={isLoading}
              className="flex-1"
            >
              이전
            </Button>
            <Button
              type="button"
              variant="danger"
              onClick={handleDeleteAccount}
              disabled={isLoading || !canDeleteAccount}
              className="flex-1"
            >
              {isLoading ? '삭제 중...' : '계정 삭제하기'}
            </Button>
          </div>
        </motion.div>
      )}
    </div>
  );
}