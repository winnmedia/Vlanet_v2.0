'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mail, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  RotateCcw,
  Loader2
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';

export interface EmailVerificationInputProps {
  email: string;
  onVerified: (verified: boolean) => void;
  onCodeChange?: (code: string) => void;
  className?: string;
  disabled?: boolean;
  // 인증 상태 및 액션 (부모에서 관리)
  verificationStatus: 'none' | 'sent' | 'verified' | 'failed';
  isVerificationLoading: boolean;
  verificationError: string | null;
  verificationCodeSentAt: number | null;
  isResendLoading: boolean;
  onVerifyCode: (code: string) => Promise<boolean>;
  onResendCode: () => Promise<boolean>;
}

/**
 * 이메일 인증 코드 입력 컴포넌트
 * 6자리 숫자 입력, 타이머, 재발송 기능 포함
 */
export function EmailVerificationInput({
  email,
  onVerified,
  onCodeChange,
  className,
  disabled = false,
  verificationStatus,
  isVerificationLoading,
  verificationError,
  verificationCodeSentAt,
  isResendLoading,
  onVerifyCode,
  onResendCode,
}: EmailVerificationInputProps) {
  const [code, setCode] = useState('');
  const [timeLeft, setTimeLeft] = useState(600); // 10분 = 600초
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // 타이머 관리
  useEffect(() => {
    if (verificationCodeSentAt && verificationStatus === 'sent') {
      const calculateTimeLeft = () => {
        const elapsed = Math.floor((Date.now() - verificationCodeSentAt) / 1000);
        return Math.max(0, 600 - elapsed); // 10분 제한
      };

      setTimeLeft(calculateTimeLeft());

      intervalRef.current = setInterval(() => {
        const newTimeLeft = calculateTimeLeft();
        setTimeLeft(newTimeLeft);
        
        if (newTimeLeft <= 0) {
          clearInterval(intervalRef.current!);
        }
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [verificationCodeSentAt, verificationStatus]);

  // 코드 변경 처리
  const handleCodeChange = useCallback((newCode: string) => {
    setCode(newCode);
    onCodeChange?.(newCode);
    
    // 6자리 완성시 자동 검증
    if (newCode.length === 6 && !disabled && !isVerificationLoading) {
      onVerifyCode(newCode).then((verified) => {
        onVerified(verified);
      });
    }
  }, [onCodeChange, onVerifyCode, onVerified, disabled, isVerificationLoading]);

  // 개별 입력 필드 변경 처리
  const handleInputChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return; // 숫자만 허용
    
    const newCode = code.split('');
    newCode[index] = value;
    const updatedCode = newCode.join('').slice(0, 6);
    
    handleCodeChange(updatedCode);

    // 다음 필드로 자동 이동
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  // 키보드 이벤트 처리
  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  // 붙여넣기 처리
  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pastedText) {
      handleCodeChange(pastedText);
      // 마지막 입력된 필드로 포커스 이동
      const focusIndex = Math.min(pastedText.length - 1, 5);
      inputRefs.current[focusIndex]?.focus();
    }
  };

  // 재발송 처리
  const handleResend = async () => {
    if (isResendLoading || timeLeft > 0) return;
    
    const success = await onResendCode();
    if (success) {
      setCode('');
      inputRefs.current[0]?.focus();
    }
  };

  // 시간 포맷팅
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 상태에 따른 색상 결정
  const getStatusColor = () => {
    switch (verificationStatus) {
      case 'verified': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'sent': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = () => {
    switch (verificationStatus) {
      case 'verified': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed': return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'sent': return <Mail className="w-5 h-5 text-blue-500" />;
      default: return <Mail className="w-5 h-5 text-gray-400" />;
    }
  };

  if (verificationStatus === 'none') {
    return null; // 인증이 시작되지 않았으면 렌더링하지 않음
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={cn('space-y-4', className)}
    >
      {/* 상태 표시 */}
      <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
        {getStatusIcon()}
        <div className="flex-1">
          <p className={cn('text-sm font-medium', getStatusColor())}>
            {verificationStatus === 'sent' && '인증 코드가 발송되었습니다'}
            {verificationStatus === 'verified' && '이메일 인증이 완료되었습니다'}
            {verificationStatus === 'failed' && '인증에 실패했습니다'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {email}로 6자리 인증 코드가 전송되었습니다
          </p>
        </div>
        {verificationStatus === 'sent' && timeLeft > 0 && (
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            {formatTime(timeLeft)}
          </div>
        )}
      </div>

      {/* 인증 코드 입력 */}
      {verificationStatus !== 'verified' && (
        <div className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            인증 코드 입력
          </label>
          
          {/* 6자리 입력 필드 */}
          <div className="flex justify-center gap-2">
            {Array.from({ length: 6 }, (_, index) => (
              <input
                key={index}
                ref={(el) => (inputRefs.current[index] = el)}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={code[index] || ''}
                onChange={(e) => handleInputChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                disabled={disabled || isVerificationLoading || verificationStatus === 'verified'}
                className={cn(
                  'w-12 h-12 text-center text-lg font-semibold border rounded-lg',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2',
                  verificationStatus === 'verified'
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : verificationStatus === 'failed'
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:ring-blue-500',
                  (disabled || isVerificationLoading) && 'bg-gray-100 cursor-not-allowed'
                )}
                aria-label={`인증 코드 ${index + 1}번째 자리`}
              />
            ))}
          </div>

          {/* 로딩 상태 */}
          <AnimatePresence>
            {isVerificationLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center gap-2 text-sm text-gray-600"
              >
                <Spinner size="sm" />
                인증 중...
              </motion.div>
            )}
          </AnimatePresence>

          {/* 에러 메시지 */}
          <AnimatePresence>
            {verificationError && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="p-3 bg-red-50 border border-red-200 rounded-lg"
              >
                <p className="text-sm text-red-600 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {verificationError}
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 재발송 버튼 */}
          <div className="flex justify-center">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleResend}
              disabled={timeLeft > 0 || isResendLoading}
              className="flex items-center gap-2"
            >
              {isResendLoading ? (
                <Spinner size="sm" />
              ) : (
                <RotateCcw className="w-4 h-4" />
              )}
              {timeLeft > 0 
                ? `${formatTime(timeLeft)} 후 재발송 가능`
                : '인증 코드 재발송'
              }
            </Button>
          </div>
        </div>
      )}

      {/* 성공 메시지 */}
      {verificationStatus === 'verified' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <p className="text-sm text-green-700 flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            이메일 인증이 성공적으로 완료되었습니다
          </p>
        </motion.div>
      )}

      {/* 도움말 */}
      <div className="text-xs text-gray-500 space-y-1">
        <p>• 인증 코드가 도착하지 않았다면 스팸 메일함을 확인해주세요</p>
        <p>• 인증 코드는 10분간 유효합니다</p>
        <p>• 코드 입력 후 자동으로 인증이 진행됩니다</p>
      </div>
    </motion.div>
  );
}