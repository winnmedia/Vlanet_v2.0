'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, Eye, EyeOff, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';

import { useAuth } from '@/contexts/auth.context';
import { 
  passwordResetRequestSchema, 
  passwordResetSchema, 
  type PasswordResetRequestData,
  type PasswordResetData 
} from '@/lib/validation/schemas';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';

export interface PasswordResetFormProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  className?: string;
}

/**
 *    
 *   →   →    2 
 */
export function PasswordResetForm({
  onSuccess,
  onError,
  className,
}: PasswordResetFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { 
    requestPasswordReset, 
    resetPassword, 
    isPasswordResetLoading, 
    passwordResetError,
    clearPasswordResetError 
  } = useAuth();

  const [step, setStep] = useState<'request' | 'reset'>('request');
  const [emailSent, setEmailSent] = useState(false);
  const [email, setEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [resetToken, setResetToken] = useState<string | null>(null);

  // URL  
  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      setResetToken(token);
      setStep('reset');
    }
  }, [searchParams]);

  //   
  const {
    register: registerRequest,
    handleSubmit: handleSubmitRequest,
    formState: { errors: requestErrors, isSubmitting: isRequestSubmitting },
    setError: setRequestError,
    clearErrors: clearRequestErrors,
  } = useForm<PasswordResetRequestData>({
    resolver: zodResolver(passwordResetRequestSchema),
    mode: 'onBlur',
  });

  //   
  const {
    register: registerReset,
    handleSubmit: handleSubmitReset,
    formState: { errors: resetErrors, isSubmitting: isResetSubmitting },
    setError: setResetError,
    clearErrors: clearResetErrors,
    watch,
  } = useForm<PasswordResetData>({
    resolver: zodResolver(passwordResetSchema),
    mode: 'onBlur',
  });

  const password = watch('password');

  //   
  const onSubmitRequest = async (data: PasswordResetRequestData) => {
    try {
      clearRequestErrors();
      clearPasswordResetError();

      const success = await requestPasswordReset(data.email);

      if (success) {
        setEmail(data.email);
        setEmailSent(true);
        onSuccess?.();
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '   .';
      
      setRequestError('root', {
        type: 'manual',
        message: errorMessage,
      });

      onError?.(error instanceof Error ? error : new Error(errorMessage));
    }
  };

  //   
  const onSubmitReset = async (data: PasswordResetData) => {
    if (!resetToken) {
      setResetError('root', {
        type: 'manual',
        message: '  .',
      });
      return;
    }

    try {
      clearResetErrors();
      clearPasswordResetError();

      const success = await resetPassword(resetToken, data.password);

      if (success) {
        //     
        setTimeout(() => {
          router.push('/login?message=password-reset-success');
        }, 2000);
        onSuccess?.();
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '  .';
      
      setResetError('root', {
        type: 'manual',
        message: errorMessage,
      });

      onError?.(error instanceof Error ? error : new Error(errorMessage));
    }
  };

  //   
  const passwordStrength = React.useMemo(() => {
    if (!password) return 0;
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    return strength;
  }, [password]);

  const getPasswordStrengthText = (strength: number) => {
    switch (strength) {
      case 0:
      case 1: return ' ';
      case 2: return '';
      case 3: return '';
      case 4: return '';
      case 5: return ' ';
      default: return '';
    }
  };

  const getPasswordStrengthColor = (strength: number) => {
    switch (strength) {
      case 0:
      case 1: return 'bg-red-500';
      case 2: return 'bg-orange-500';
      case 3: return 'bg-yellow-500';
      case 4: return 'bg-green-500';
      case 5: return 'bg-emerald-500';
      default: return 'bg-gray-200';
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const togglePasswordConfirmVisibility = () => {
    setShowPasswordConfirm(!showPasswordConfirm);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn('w-full max-w-md mx-auto', className)}
    >
      <AnimatePresence mode="wait">
        {step === 'request' && !emailSent && (
          <motion.div
            key="request-form"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center space-y-3">
              <h1 className="text-2xl font-bold text-gray-900"> </h1>
              <p className="text-gray-600">
                   <br />
                   .
              </p>
            </div>

            <form onSubmit={handleSubmitRequest(onSubmitRequest)} className="space-y-6">
              {/*   */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                   
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Mail className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...registerRequest('email')}
                    type="email"
                    id="email"
                    className={cn(
                      'w-full pl-10 pr-4 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      'placeholder:text-gray-400',
                      requestErrors.email
                        ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                        : 'border-gray-300 focus:ring-brand-primary focus:border-brand-primary'
                    )}
                    placeholder="name@company.com"
                    autoComplete="email"
                    aria-invalid={!!requestErrors.email}
                    aria-describedby={requestErrors.email ? 'email-error' : undefined}
                  />
                </div>
                <AnimatePresence>
                  {requestErrors.email && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      id="email-error"
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {requestErrors.email.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*    */}
              <AnimatePresence>
                {(requestErrors.root || passwordResetError) && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="p-4 bg-red-50 border border-red-200 rounded-lg"
                  >
                    <p className="text-sm text-red-600 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      {requestErrors.root?.message || passwordResetError}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/*   */}
              <Button
                type="submit"
                disabled={isRequestSubmitting || isPasswordResetLoading}
                className="w-full"
                size="lg"
              >
                {isRequestSubmitting || isPasswordResetLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Spinner size="sm" color="white" />
                     ...
                  </span>
                ) : (
                  '  '
                )}
              </Button>
            </form>

            {/*    */}
            <div className="text-center">
              <a 
                href="/login"
                className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                  
              </a>
            </div>
          </motion.div>
        )}

        {step === 'request' && emailSent && (
          <motion.div
            key="email-sent"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="text-center space-y-6"
          >
            <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            
            <div className="space-y-3">
              <h1 className="text-2xl font-bold text-gray-900"> </h1>
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-medium text-brand-primary">{email}</span><br />
                     .
                </p>
                <p className="text-sm text-gray-500">
                      .
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <Button
                onClick={() => {
                  setEmailSent(false);
                  clearRequestErrors();
                  clearPasswordResetError();
                }}
                variant="outline"
                className="w-full"
              >
                 
              </Button>
              
              <a 
                href="/login"
                className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                  
              </a>
            </div>
          </motion.div>
        )}

        {step === 'reset' && (
          <motion.div
            key="reset-form"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center space-y-3">
              <h1 className="text-2xl font-bold text-gray-900">  </h1>
              <p className="text-gray-600">
                  .
              </p>
            </div>

            <form onSubmit={handleSubmitReset(onSubmitReset)} className="space-y-6">
              <input
                {...registerReset('token')}
                type="hidden"
                value={resetToken || ''}
              />

              {/*   */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                   
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...registerReset('password')}
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    className={cn(
                      'w-full pl-10 pr-12 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      resetErrors.password
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-300 focus:ring-brand-primary'
                    )}
                    placeholder="8 , , ,  "
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>

                {/*    */}
                {password && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className={cn(
                            'h-full rounded-full transition-all duration-300',
                            getPasswordStrengthColor(passwordStrength)
                          )}
                          style={{ width: `${(passwordStrength / 5) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600 min-w-16">
                        {getPasswordStrengthText(passwordStrength)}
                      </span>
                    </div>
                  </div>
                )}

                <AnimatePresence>
                  {resetErrors.password && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {resetErrors.password.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*   */}
              <div className="space-y-2">
                <label htmlFor="passwordConfirm" className="block text-sm font-medium text-gray-700">
                   
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...registerReset('passwordConfirm')}
                    type={showPasswordConfirm ? 'text' : 'password'}
                    id="passwordConfirm"
                    className={cn(
                      'w-full pl-10 pr-12 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      resetErrors.passwordConfirm
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-300 focus:ring-brand-primary'
                    )}
                    placeholder="  "
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordConfirmVisibility}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPasswordConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <AnimatePresence>
                  {resetErrors.passwordConfirm && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {resetErrors.passwordConfirm.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*    */}
              <AnimatePresence>
                {(resetErrors.root || passwordResetError) && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="p-4 bg-red-50 border border-red-200 rounded-lg"
                  >
                    <p className="text-sm text-red-600 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      {resetErrors.root?.message || passwordResetError}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/*   */}
              <Button
                type="submit"
                disabled={isResetSubmitting || isPasswordResetLoading}
                className="w-full"
                size="lg"
              >
                {isResetSubmitting || isPasswordResetLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Spinner size="sm" color="white" />
                     ...
                  </span>
                ) : (
                  ' '
                )}
              </Button>
            </form>

            {/*    */}
            <div className="text-center">
              <a 
                href="/login"
                className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-brand-primary transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                  
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}