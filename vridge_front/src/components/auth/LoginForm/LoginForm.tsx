'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, Mail, Lock, AlertCircle } from 'lucide-react';

import { useAuth } from '@/contexts/auth.context';
import { loginSchema, type LoginFormData } from '@/lib/validation/schemas';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Spinner';

export interface LoginFormProps {
  onSuccess?: (user: any) => void;
  onError?: (error: Error) => void;
  redirectTo?: string;
  showSocialLogin?: boolean;
  showRememberMe?: boolean;
  className?: string;
}

/**
 *   
 * React Hook Form + Zod     
 *      UI
 */
export function LoginForm({
  onSuccess,
  onError,
  redirectTo = '/dashboard',
  showSocialLogin = true,
  showRememberMe = true,
  className,
}: LoginFormProps) {
  const router = useRouter();
  const { login, isLoginLoading, loginError, clearLoginError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, touchedFields },
    setError,
    clearErrors,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur',
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearErrors();
      clearLoginError();

      const success = await login({
        email: data.email,
        password: data.password,
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

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleSocialLogin = (provider: 'google' | 'kakao') => {
    //    
    console.log(`${provider} login clicked`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn('w-full max-w-md mx-auto', className)}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/*    */}
        <div className="space-y-2">
          <label 
            htmlFor="email" 
            className="block text-sm font-medium text-gray-700"
          >
            
            <span className="text-red-500 ml-1">*</span>
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
                'w-full pl-10 pr-4 py-2.5 rounded-lg border transition-colors duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2',
                'placeholder:text-gray-400',
                errors.email
                  ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                  : touchedFields.email
                  ? 'border-green-500 focus:ring-green-500 focus:border-green-500'
                  : 'border-gray-300 focus:ring-brand-primary focus:border-brand-primary'
              )}
              placeholder="name@company.com"
              autoComplete="email"
              aria-invalid={!!errors.email}
              aria-describedby={errors.email ? 'email-error' : undefined}
            />
          </div>
          
          <AnimatePresence mode="wait">
            {errors.email && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                id="email-error"
                className="text-sm text-red-500 flex items-center gap-1"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {errors.email.message}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        {/*    */}
        <div className="space-y-2">
          <label 
            htmlFor="password" 
            className="block text-sm font-medium text-gray-700"
          >
            
            <span className="text-red-500 ml-1">*</span>
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
                'placeholder:text-gray-400',
                errors.password
                  ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
                  : 'border-gray-300 focus:ring-brand-primary focus:border-brand-primary'
              )}
              placeholder="••••••••"
              autoComplete="current-password"
              aria-invalid={!!errors.password}
              aria-describedby={errors.password ? 'password-error' : undefined}
            />
            
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label={showPassword ? ' ' : ' '}
            >
              {showPassword ? (
                <EyeOff className="w-5 h-5" />
              ) : (
                <Eye className="w-5 h-5" />
              )}
            </button>
          </div>
          
          <AnimatePresence mode="wait">
            {errors.password && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                id="password-error"
                className="text-sm text-red-500 flex items-center gap-1"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {errors.password.message}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        {/*  &   */}
        {showRememberMe && (
          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                {...register('rememberMe')}
                type="checkbox"
                className="w-4 h-4 text-brand-primary border-gray-300 rounded focus:ring-brand-primary focus:ring-2"
              />
              <span className="ml-2 text-sm text-gray-600">  </span>
            </label>
            
            <a 
              href="/reset-password" 
              className="text-sm text-brand-primary hover:text-brand-primary-dark transition-colors"
            >
               
            </a>
          </div>
        )}

        {/*    */}
        <AnimatePresence mode="wait">
          {(errors.root || loginError) && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="p-4 bg-red-50 border border-red-200 rounded-lg"
            >
              <p className="text-sm text-red-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {errors.root?.message || loginError}
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/*   */}
        <Button
          type="submit"
          disabled={isSubmitting || isLoginLoading}
          className="w-full"
          size="lg"
        >
          {isSubmitting || isLoginLoading ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner size="sm" color="white" />
               ...
            </span>
          ) : (
            ''
          )}
        </Button>

        {/*   */}
        {showSocialLogin && (
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
                disabled={isSubmitting || isLoginLoading}
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
                disabled={isSubmitting || isLoginLoading}
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
        <p className="text-center text-sm text-gray-600">
            ?{' '}
          <a 
            href="/signup" 
            className="font-medium text-brand-primary hover:text-brand-primary-dark transition-colors"
          >
            
          </a>
        </p>
      </form>
    </motion.div>
  );
}