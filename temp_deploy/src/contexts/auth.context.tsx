'use client';

import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAuthStore } from '@/store/auth.store';
import { tokenManager } from '@/lib/auth/token-manager';
import type { User, LoginRequest, SignupRequest } from '@/types';

/**
 * 인증 컨텍스트 타입 정의
 * Zustand 스토어와 일치하는 인터페이스 제공
 */
interface AuthContextType {
  // 기본 상태
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  
  // 세부 로딩 상태
  isLoginLoading: boolean;
  isSignupLoading: boolean;
  isPasswordResetLoading: boolean;
  
  // 에러 상태
  loginError: string | null;
  signupError: string | null;
  passwordResetError: string | null;
  
  // 기본 인증 액션
  login: (credentials: LoginRequest) => Promise<boolean>;
  signup: (data: SignupRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  
  // 비밀번호 관리
  requestPasswordReset: (email: string) => Promise<boolean>;
  resetPassword: (token: string, newPassword: string) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  
  // 프로필 관리
  updateProfile: (data: Partial<User>) => Promise<boolean>;
  
  // 유효성 검사
  checkEmailAvailability: (email: string) => Promise<void>;
  checkNicknameAvailability: (nickname: string) => Promise<void>;
  
  // 권한 관리
  hasPermission: () => boolean;
  
  // 유효성 검사 결과
  emailCheckResult: any;
  nicknameCheckResult: any;
  isEmailCheckLoading: boolean;
  isNicknameCheckLoading: boolean;
  
  // 소셜 로그인
  loginWithGoogle: () => Promise<void>;
  loginWithKakao: () => Promise<void>;
  handleSocialLoginCallback: (provider: 'google' | 'kakao', code: string, state: string) => Promise<boolean>;
  
  // 에러 관리
  clearError: () => void;
  clearLoginError: () => void;
  clearSignupError: () => void;
  clearPasswordResetError: () => void;
  
  // 상태 초기화
  reset: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * 인증 프로바이더 컴포넌트
 * Zustand 스토어와 연동하여 전역 인증 상태 관리
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const authStore = useAuthStore();
  const checkAuthStatus = useAuthStore(state => state.checkAuthStatus);
  const reset = useAuthStore(state => state.reset);
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);

  useEffect(() => {
    // 컴포넌트 마운트 시 한 번만 인증 상태 확인
    let mounted = true;
    
    const initAuth = async () => {
      if (mounted) {
        await checkAuthStatus();
      }
    };
    
    initAuth();

    // 토큰 매니저의 인증 실패 이벤트 리스너 등록
    const handleAuthFailure = () => {
      reset();
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('auth:failure', handleAuthFailure);
      
      // 페이지 가시성 변경 시 토큰 상태 재확인
      const handleVisibilityChange = () => {
        if (document.visibilityState === 'visible' && isAuthenticated) {
          // 토큰이 만료되었는지 확인
          if (!tokenManager.isAuthenticated()) {
            reset();
          }
        }
      };

      document.addEventListener('visibilitychange', handleVisibilityChange);

      return () => {
        mounted = false;
        window.removeEventListener('auth:failure', handleAuthFailure);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
      };
    }
    
    return () => {
      mounted = false;
    };
  }, [checkAuthStatus, reset]); // 필요한 함수만 의존성 배열에 추가

  // Zustand 스토어의 모든 상태와 액션을 컨텍스트에 제공
  const contextValue: AuthContextType = {
    // 기본 상태
    user: authStore.user,
    isLoading: authStore.isLoading,
    isAuthenticated: authStore.isAuthenticated,
    error: authStore.error,
    
    // 세부 로딩 상태
    isLoginLoading: authStore.isLoginLoading,
    isSignupLoading: authStore.isSignupLoading,
    isPasswordResetLoading: authStore.isPasswordResetLoading,
    
    // 에러 상태
    loginError: authStore.loginError,
    signupError: authStore.signupError,
    passwordResetError: authStore.passwordResetError,
    
    // 액션들
    login: authStore.login,
    signup: authStore.signup,
    logout: authStore.logout,
    refreshUser: authStore.refreshUser,
    checkAuthStatus: authStore.checkAuthStatus,
    
    requestPasswordReset: authStore.requestPasswordReset,
    resetPassword: authStore.resetPassword,
    changePassword: authStore.changePassword,
    
    updateProfile: authStore.updateProfile,
    
    checkEmailAvailability: authStore.checkEmailAvailability,
    checkNicknameAvailability: authStore.checkNicknameAvailability,
    
    // 인증 상태 관련 추가 필드들
    hasPermission: () => true, // 임시 구현
    emailCheckResult: null, // 임시 구현
    nicknameCheckResult: null, // 임시 구현
    isEmailCheckLoading: false, // 임시 구현
    isNicknameCheckLoading: false, // 임시 구현
    
    loginWithGoogle: authStore.loginWithGoogle,
    loginWithKakao: authStore.loginWithKakao,
    handleSocialLoginCallback: authStore.handleSocialLoginCallback,
    
    clearError: authStore.clearError,
    clearLoginError: authStore.clearLoginError,
    clearSignupError: authStore.clearSignupError,
    clearPasswordResetError: authStore.clearPasswordResetError,
    
    reset: authStore.reset,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * 인증 컨텍스트 훅
 * 컴포넌트에서 인증 상태와 액션에 접근하기 위한 훅
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * 인증이 필요한 컴포넌트에서 사용하는 훅
 * 사용자가 로그인하지 않은 경우 에러를 발생시킵니다.
 */
export function useRequireAuth(): AuthContextType & { user: User } {
  const auth = useAuth();
  
  if (!auth.isAuthenticated || !auth.user) {
    throw new Error('This component requires authentication');
  }
  
  return auth as AuthContextType & { user: User };
}

/**
 * 로그인 상태를 확인하는 유틸리티 훅
 */
export function useAuthStatus() {
  const { isAuthenticated, isLoading, user } = useAuth();
  
  return {
    isAuthenticated,
    isLoading,
    isLoggedIn: isAuthenticated && !!user,
    isGuest: !isAuthenticated || !user,
    userId: user?.id || null,
  };
}