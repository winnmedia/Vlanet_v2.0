'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  Phone, 
  Building, 
  AlertCircle,
  CheckCircle,
  X
} from 'lucide-react';
// debounce  
const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

import { useAuth } from '@/contexts/auth.context';
import { signupSchema, type SignupFormData } from '@/lib/validation/schemas';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';

export interface SignupFormProps {
  onSuccess?: (user: any) => void;
  onError?: (error: Error) => void;
  redirectTo?: string;
  showSocialLogin?: boolean;
  className?: string;
}

/**
 *   
 *  ,  ,     UI
 */
export function SignupForm({
  onSuccess,
  onError,
  redirectTo = '/dashboard',
  showSocialLogin = true,
  className,
}: SignupFormProps) {
  const router = useRouter();
  const { 
    signup, 
    isSignupLoading, 
    signupError, 
    clearSignupError,
    checkEmailAvailability,
    checkNicknameAvailability,
    emailCheckResult,
    nicknameCheckResult,
    isEmailCheckLoading,
    isNicknameCheckLoading,
  } = useAuth();
  
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, touchedFields },
    setError,
    clearErrors,
    control,
    trigger,
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    mode: 'onBlur',
    defaultValues: {
      agreedToTerms: false,
      agreedToPrivacy: false,
      agreedToMarketing: false,
    },
  });

  const watchedEmail = watch('email');
  const watchedNickname = watch('nickname');
  const password = watch('password');

  //    ()
  const debouncedEmailCheck = useCallback(
    debounce(async (email: string) => {
      if (email && !errors.email) {
        await checkEmailAvailability(email);
      }
    }, 500),
    [checkEmailAvailability, errors.email]
  );

  //    ()
  const debouncedNicknameCheck = useCallback(
    debounce(async (nickname: string) => {
      if (nickname && !errors.nickname) {
        await checkNicknameAvailability(nickname);
      }
    }, 500),
    [checkNicknameAvailability, errors.nickname]
  );

  React.useEffect(() => {
    if (touchedFields.email && watchedEmail) {
      debouncedEmailCheck(watchedEmail);
    }
  }, [watchedEmail, touchedFields.email, debouncedEmailCheck]);

  React.useEffect(() => {
    if (touchedFields.nickname && watchedNickname) {
      debouncedNicknameCheck(watchedNickname);
    }
  }, [watchedNickname, touchedFields.nickname, debouncedNicknameCheck]);

  const onSubmit = async (data: SignupFormData) => {
    try {
      clearErrors();
      clearSignupError();

      const success = await signup({
        email: data.email,
        password: data.password,
        nickname: data.nickname,
        phone: data.phone,
        company: data.company,
      });

      if (success) {
        onSuccess?.(data);
        router.push(redirectTo);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : ' .';
      
      setError('root', {
        type: 'manual',
        message: errorMessage,
      });

      onError?.(error instanceof Error ? error : new Error(errorMessage));
    }
  };

  const handleNextStep = async () => {
    const step1Fields = ['email', 'nickname', 'password', 'passwordConfirm'] as const;
    const isValid = await trigger(step1Fields);
    
    if (isValid && emailCheckResult?.available && nicknameCheckResult?.available) {
      setCurrentStep(2);
    }
  };

  const handlePrevStep = () => {
    setCurrentStep(1);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const togglePasswordConfirmVisibility = () => {
    setShowPasswordConfirm(!showPasswordConfirm);
  };

  const handleSocialLogin = (provider: 'google' | 'kakao') => {
    //    
    console.log(`${provider} signup clicked`);
  };

  const getEmailValidationStatus = () => {
    if (errors.email) return 'error';
    if (isEmailCheckLoading) return 'loading';
    if (emailCheckResult?.available === false) return 'error';
    if (emailCheckResult?.available === true) return 'success';
    return 'default';
  };

  const getNicknameValidationStatus = () => {
    if (errors.nickname) return 'error';
    if (isNicknameCheckLoading) return 'loading';
    if (nicknameCheckResult?.available === false) return 'error';
    if (nicknameCheckResult?.available === true) return 'success';
    return 'default';
  };

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

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn('w-full max-w-lg mx-auto', className)}
    >
      {/*   */}
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center">
          <div className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
            currentStep === 1 ? 'bg-brand-primary text-white' : 'bg-gray-200 text-gray-600'
          )}>
            1
          </div>
          <div className="w-12 h-0.5 bg-gray-200 mx-2" />
          <div className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
            currentStep === 2 ? 'bg-brand-primary text-white' : 'bg-gray-200 text-gray-600'
          )}>
            2
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* 1:   */}
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2"> </h2>
                <p className="text-gray-600">   </p>
              </div>

              {/*  */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                   <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Mail className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...register('email')}
                    type="email"
                    id="email"
                    className={cn(
                      'w-full pl-10 pr-10 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      getEmailValidationStatus() === 'error'
                        ? 'border-red-500 focus:ring-red-500'
                        : getEmailValidationStatus() === 'success'
                        ? 'border-green-500 focus:ring-green-500'
                        : 'border-gray-300 focus:ring-brand-primary'
                    )}
                    placeholder="name@company.com"
                    autoComplete="email"
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {isEmailCheckLoading ? (
                      <Spinner size="sm" />
                    ) : getEmailValidationStatus() === 'success' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : getEmailValidationStatus() === 'error' ? (
                      <X className="w-5 h-5 text-red-500" />
                    ) : null}
                  </div>
                </div>
                <AnimatePresence>
                  {(errors.email || emailCheckResult?.available === false) && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {errors.email?.message || emailCheckResult?.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*  */}
              <div className="space-y-2">
                <label htmlFor="nickname" className="block text-sm font-medium text-gray-700">
                   <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <User className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...register('nickname')}
                    type="text"
                    id="nickname"
                    className={cn(
                      'w-full pl-10 pr-10 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      getNicknameValidationStatus() === 'error'
                        ? 'border-red-500 focus:ring-red-500'
                        : getNicknameValidationStatus() === 'success'
                        ? 'border-green-500 focus:ring-green-500'
                        : 'border-gray-300 focus:ring-brand-primary'
                    )}
                    placeholder="  "
                    autoComplete="username"
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {isNicknameCheckLoading ? (
                      <Spinner size="sm" />
                    ) : getNicknameValidationStatus() === 'success' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : getNicknameValidationStatus() === 'error' ? (
                      <X className="w-5 h-5 text-red-500" />
                    ) : null}
                  </div>
                </div>
                <AnimatePresence>
                  {(errors.nickname || nicknameCheckResult?.available === false) && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {errors.nickname?.message || nicknameCheckResult?.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*  */}
              <div className="space-y-2">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                   <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...register('password')}
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    className={cn(
                      'w-full pl-10 pr-12 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      errors.password
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-300 focus:ring-brand-primary'
                    )}
                    placeholder="8 , , ,  "
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-2 min-w-[48px] min-h-[48px] flex items-center justify-center"
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
                  {errors.password && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {errors.password.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*   */}
              <div className="space-y-2">
                <label htmlFor="passwordConfirm" className="block text-sm font-medium text-gray-700">
                    <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Lock className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...register('passwordConfirm')}
                    type={showPasswordConfirm ? 'text' : 'password'}
                    id="passwordConfirm"
                    className={cn(
                      'w-full pl-10 pr-12 py-2.5 rounded-lg border transition-colors duration-200',
                      'focus:outline-none focus:ring-2 focus:ring-offset-2',
                      errors.passwordConfirm
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-300 focus:ring-brand-primary'
                    )}
                    placeholder="  "
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordConfirmVisibility}
                    className="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-2 min-w-[48px] min-h-[48px] flex items-center justify-center"
                  >
                    {showPasswordConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <AnimatePresence>
                  {errors.passwordConfirm && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {errors.passwordConfirm.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              <Button
                type="button"
                onClick={handleNextStep}
                className="w-full"
                size="lg"
              >
                 
              </Button>
            </motion.div>
          )}

          {/* 2:      */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2"> </h2>
                <p className="text-gray-600">    </p>
              </div>

              {/*  */}
              <div className="space-y-2">
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Phone className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...register('phone')}
                    type="tel"
                    id="phone"
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary"
                    placeholder="010-0000-0000"
                    autoComplete="tel"
                  />
                </div>
                <AnimatePresence>
                  {errors.phone && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {errors.phone.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*  */}
              <div className="space-y-2">
                <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                  
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 -translate-y-1/2">
                    <Building className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    {...register('company')}
                    type="text"
                    id="company"
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary"
                    placeholder=" "
                    autoComplete="organization"
                  />
                </div>
                <AnimatePresence>
                  {errors.company && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                      {errors.company.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*   */}
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-medium text-gray-900"> </h3>
                
                <Controller
                  name="agreedToTerms"
                  control={control}
                  render={({ field }) => (
                    <label className="flex items-start gap-3 cursor-pointer min-h-[48px]">
                      <input
                        type="checkbox"
                        checked={field.value}
                        onChange={field.onChange}
                        className="mt-2 w-5 h-5 text-brand-primary border-gray-300 rounded focus:ring-brand-primary focus:ring-2 cursor-pointer"
                      />
                      <div className="flex-1">
                        <span className="text-sm text-gray-900">
                          <span className="text-red-500">*</span>  
                        </span>
                        <a href="/terms" target="_blank" className="text-brand-primary hover:underline ml-2 text-sm">
                          
                        </a>
                      </div>
                    </label>
                  )}
                />

                <Controller
                  name="agreedToPrivacy"
                  control={control}
                  render={({ field }) => (
                    <label className="flex items-start gap-3 cursor-pointer min-h-[48px]">
                      <input
                        type="checkbox"
                        checked={field.value}
                        onChange={field.onChange}
                        className="mt-2 w-5 h-5 text-brand-primary border-gray-300 rounded focus:ring-brand-primary focus:ring-2 cursor-pointer"
                      />
                      <div className="flex-1">
                        <span className="text-sm text-gray-900">
                          <span className="text-red-500">*</span>  
                        </span>
                        <a href="/privacy" target="_blank" className="text-brand-primary hover:underline ml-2 text-sm">
                          
                        </a>
                      </div>
                    </label>
                  )}
                />

                <Controller
                  name="agreedToMarketing"
                  control={control}
                  render={({ field }) => (
                    <label className="flex items-start gap-3 cursor-pointer min-h-[48px]">
                      <input
                        type="checkbox"
                        checked={field.value}
                        onChange={field.onChange}
                        className="mt-2 w-5 h-5 text-brand-primary border-gray-300 rounded focus:ring-brand-primary focus:ring-2 cursor-pointer"
                      />
                      <div className="flex-1">
                        <span className="text-sm text-gray-900">
                              ()
                        </span>
                      </div>
                    </label>
                  )}
                />

                <AnimatePresence>
                  {(errors.agreedToTerms || errors.agreedToPrivacy) && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle className="w-4 h-4" />
                        
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              {/*    */}
              <AnimatePresence>
                {(errors.root || signupError) && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="p-4 bg-red-50 border border-red-200 rounded-lg"
                  >
                    <p className="text-sm text-red-600 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      {errors.root?.message || signupError}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/*   */}
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handlePrevStep}
                  className="flex-1"
                  size="lg"
                >
                  
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || isSignupLoading}
                  className="flex-1"
                  size="lg"
                >
                  {isSubmitting || isSignupLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Spinner size="sm" color="white" />
                       ...
                    </span>
                  ) : (
                    ' '
                  )}
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/*   (1 ) */}
        {showSocialLogin && currentStep === 1 && (
          <>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500"></span>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => handleSocialLogin('google')}
                disabled={isSubmitting || isSignupLoading}
                className="w-full"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Google
              </Button>
              
              <Button
                type="button"
                variant="outline"
                onClick={() => handleSocialLogin('kakao')}
                disabled={isSubmitting || isSignupLoading}
                className="w-full"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 0 1-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3Z"
                  />
                </svg>
                Kakao
              </Button>
            </div>
          </>
        )}

        {/*   */}
        {currentStep === 1 && (
          <p className="text-center text-sm text-gray-600">
              ?{' '}
            <a 
              href="/login" 
              className="font-medium text-brand-primary hover:text-brand-primary-dark transition-colors"
            >
              
            </a>
          </p>
        )}
      </form>
    </motion.div>
  );
}