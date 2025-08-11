'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

type FindType = 'username' | 'password';

interface FindAccountFormProps {
  type: FindType;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function FindAccountForm({ type, onSuccess, onError }: FindAccountFormProps) {
  const [step, setStep] = useState<'email' | 'code' | 'newPassword'>('email');
  const [email, setEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);

  const isUsernameFind = type === 'username';
  const isPasswordReset = type === 'password';

  //      
  const handleSendRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccessMessage('');

    const endpoint = isUsernameFind 
      ? '/api/users/account/find-username/'
      : '/api/users/account/password-reset/request/';

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await response.json();

      if (data.success) {
        if (isUsernameFind) {
          setSuccessMessage('   .');
          onSuccess?.();
        } else {
          setStep('code');
          startResendCooldown();
        }
      } else {
        setError(data.message || '  .');
        onError?.(new Error(data.message));
      }
    } catch (err) {
      const error = err as Error;
      setError('  .');
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  //    ( )
  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (verificationCode.length !== 6) {
      setError('6   .');
      return;
    }
    setStep('newPassword');
  };

  //   
  const handleSetNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError('  .');
      return;
    }

    if (newPassword.length < 8) {
      setError(' 8  .');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/account/password-reset/confirm/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email.trim(), 
          verification_code: verificationCode.trim(),
          new_password: newPassword 
        }),
      });

      const data = await response.json();

      if (data.success) {
        setSuccessMessage('  .');
        onSuccess?.();
      } else {
        setError(data.message || '  .');
        onError?.(new Error(data.message));
      }
    } catch (err) {
      const error = err as Error;
      setError('  .');
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  //   
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

  //   
  const handleResendCode = async () => {
    if (resendCooldown > 0) return;
    
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/account/password-reset/request/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email.trim() }),
      });

      const data = await response.json();

      if (data.success) {
        startResendCooldown();
        alert('  .');
      } else {
        setError(data.message || ' .');
      }
    } catch (err) {
      setError('  .');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/*   */}
      {successMessage && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-green-50 border border-green-200 rounded-lg p-4"
        >
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium text-green-800">{successMessage}</span>
          </div>
        </motion.div>
      )}

      <AnimatePresence mode="wait">
        {step === 'email' ? (
          <motion.form
            key="email-form"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            onSubmit={handleSendRequest}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {isUsernameFind ? ' ' : ' '}
              </label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="    "
                required
                disabled={isLoading}
                className="w-full"
              />
              <p className="mt-1 text-xs text-gray-500">
                {isUsernameFind 
                  ? '       .'
                  : '       .'
                }
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
              {isLoading 
                ? (isUsernameFind ? '  ...' : '   ...') 
                : (isUsernameFind ? ' ' : '  ')
              }
            </Button>
          </motion.form>
        ) : step === 'code' ? (
          <motion.form
            key="code-form"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            onSubmit={handleVerifyCode}
            className="space-y-4"
          >
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <span className="font-medium text-blue-800">  !</span>
              </div>
              <p className="text-sm text-blue-700">
                <span className="font-medium">{email}</span>  6   .
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                 
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
                  10 .
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
                 
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1"
                disabled={isLoading || verificationCode.length !== 6}
              >
                {isLoading ? ' ...' : ''}
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
                  ? ` ${resendCooldown}` 
                  : '  '
                }
              </button>
            </div>
          </motion.form>
        ) : (
          <motion.form
            key="password-form"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            onSubmit={handleSetNewPassword}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                 
              </label>
              <Input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="  (8 )"
                required
                disabled={isLoading}
                className="w-full"
                minLength={8}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                 
              </label>
              <Input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="  "
                required
                disabled={isLoading}
                className="w-full"
                minLength={8}
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

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <svg className="w-4 h-4 text-yellow-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div className="text-xs text-yellow-800">
                  <p className="font-medium mb-1"> </p>
                  <ul className="space-y-0.5">
                    <li>• 8  </li>
                    <li>•    </li>
                    <li>•   </li>
                  </ul>
                </div>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={isLoading || !newPassword || !confirmPassword || newPassword !== confirmPassword}
            >
              {isLoading ? '  ...' : ' '}
            </Button>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}