'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/auth.context';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { AUTH_MESSAGES } from '@/utils/constants/messages';

export interface SocialLoginButtonsProps {
  mode?: 'login' | 'signup';
  onSuccess?: (provider: 'google' | 'kakao') => void;
  onError?: (error: Error) => void;
  disabled?: boolean;
  className?: string;
}

/**
 *    
 * Google, Kakao       
 */
export function SocialLoginButtons({
  mode = 'login',
  onSuccess,
  onError,
  disabled = false,
  className,
}: SocialLoginButtonsProps) {
  const { loginWithGoogle, loginWithKakao, isLoading } = useAuth();
  const [loadingProvider, setLoadingProvider] = useState<'google' | 'kakao' | null>(null);

  const handleGoogleLogin = async () => {
    if (disabled || loadingProvider) return;

    //    
    alert(AUTH_MESSAGES.GOOGLE_LOGIN_PREPARING);
    return;

    // TODO:        
    /*
    try {
      setLoadingProvider('google');
      await loginWithGoogle();
      onSuccess?.('google');
    } catch (error) {
      const errorMessage = error instanceof Error ? error : new Error('Google  .');
      onError?.(errorMessage);
    } finally {
      setLoadingProvider(null);
    }
    */
  };

  const handleKakaoLogin = async () => {
    if (disabled || loadingProvider) return;

    //    
    alert(AUTH_MESSAGES.KAKAO_LOGIN_PREPARING);
    return;

    // TODO:        
    /*
    try {
      setLoadingProvider('kakao');
      await loginWithKakao();
      onSuccess?.('kakao');
    } catch (error) {
      const errorMessage = error instanceof Error ? error : new Error('Kakao  .');
      onError?.(errorMessage);
    } finally {
      setLoadingProvider(null);
    }
    */
  };

  const isDisabled = disabled || isLoading || !!loadingProvider;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn('space-y-3', className)}
    >
      {/*  */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-white text-gray-500">
            {mode === 'signup' ? ' ' : ' '}
          </span>
        </div>
      </div>

      {/*    */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Google  */}
        <Button
          type="button"
          variant="outline"
          onClick={handleGoogleLogin}
          disabled={true} //  
          className={cn(
            'w-full h-12 text-gray-700',
            'border-gray-300 hover:border-gray-400',
            'hover:bg-gray-50 transition-colors duration-200',
            'opacity-60 cursor-not-allowed', //  
            loadingProvider === 'google' && 'bg-gray-50'
          )}
        >
          <>
            <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Google {mode === 'signup' ? '' : ''} ()
          </>
        </Button>

        {/* Kakao  */}
        <Button
          type="button"
          onClick={handleKakaoLogin}
          disabled={true} //  
          className={cn(
            'w-full h-12 text-gray-900 font-medium',
            'bg-[#FEE500] hover:bg-[#FEE500]/90',
            'border border-[#FEE500] hover:border-[#FEE500]/90',
            'shadow-sm hover:shadow-md transition-all duration-200',
            'opacity-60 cursor-not-allowed', //  
            loadingProvider === 'kakao' && 'bg-[#FEE500]/80'
          )}
        >
          <>
            <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 0 1-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3Z"
              />
            </svg>
            Kakao {mode === 'signup' ? '' : ''} ()
          </>
        </Button>
      </div>

      {/*    */}
      <p className="text-center text-xs text-gray-500 mt-4">
         {mode === 'signup' ? '' : ''} {' '}
        <a 
          href="/terms" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-brand-primary hover:underline"
        >
          
        </a>
        {' '}{' '}
        <a 
          href="/privacy" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-brand-primary hover:underline"
        >
          
        </a>
          .
      </p>
    </motion.div>
  );
}

/**
 *     
 */
interface SocialLoginButtonProps {
  provider: 'google' | 'kakao';
  mode?: 'login' | 'signup';
  onClick?: () => void;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
}

export function SocialLoginButton({
  provider,
  mode = 'login',
  onClick,
  loading = false,
  disabled = false,
  className,
}: SocialLoginButtonProps) {
  const getSocialIcon = (provider: 'google' | 'kakao') => {
    switch (provider) {
      case 'google':
        return (
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
        );
      case 'kakao':
        return (
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 0 1-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3Z"
            />
          </svg>
        );
    }
  };

  const getSocialLabel = (provider: 'google' | 'kakao', mode: 'login' | 'signup') => {
    const action = mode === 'signup' ? '' : '';
    switch (provider) {
      case 'google':
        return `Google ${action}`;
      case 'kakao':
        return `Kakao ${action}`;
    }
  };

  const getSocialStyles = (provider: 'google' | 'kakao') => {
    switch (provider) {
      case 'google':
        return 'bg-white hover:bg-gray-50 border border-gray-300 text-gray-700';
      case 'kakao':
        return 'bg-[#FEE500] hover:bg-[#FEE500]/90 border border-[#FEE500] text-gray-900';
    }
  };

  return (
    <Button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        'w-full h-12 font-medium',
        'transition-all duration-200',
        getSocialStyles(provider),
        loading && 'opacity-75 cursor-not-allowed',
        className
      )}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <Spinner size="sm" color="gray" />
           ...
        </span>
      ) : (
        <span className="flex items-center justify-center gap-3">
          {getSocialIcon(provider)}
          {getSocialLabel(provider, mode)}
        </span>
      )}
    </Button>
  );
}