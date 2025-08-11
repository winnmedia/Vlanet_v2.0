'use client';

import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAuthStore } from '@/store/auth.store';
import { tokenManager } from '@/lib/auth/token-manager';
import type { User, LoginRequest, SignupRequest } from '@/types';

/**
 *    
 * Zustand    
 */
interface AuthContextType {
  //  
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  
  //   
  isLoginLoading: boolean;
  isSignupLoading: boolean;
  isPasswordResetLoading: boolean;
  
  //  
  loginError: string | null;
  signupError: string | null;
  passwordResetError: string | null;
  
  //   
  login: (credentials: LoginRequest) => Promise<boolean>;
  signup: (data: SignupRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  
  //  
  requestPasswordReset: (email: string) => Promise<boolean>;
  resetPassword: (token: string, newPassword: string) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  
  //  
  updateProfile: (data: Partial<User>) => Promise<boolean>;
  
  //  
  checkEmailAvailability: (email: string) => Promise<void>;
  checkNicknameAvailability: (nickname: string) => Promise<void>;
  
  //  
  hasPermission: () => boolean;
  
  //   
  emailCheckResult: any;
  nicknameCheckResult: any;
  isEmailCheckLoading: boolean;
  isNicknameCheckLoading: boolean;
  
  //  
  loginWithGoogle: () => Promise<void>;
  loginWithKakao: () => Promise<void>;
  handleSocialLoginCallback: (provider: 'google' | 'kakao', code: string, state: string) => Promise<boolean>;
  
  //  
  clearError: () => void;
  clearLoginError: () => void;
  clearSignupError: () => void;
  clearPasswordResetError: () => void;
  
  //  
  reset: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 *   
 * Zustand      
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const authStore = useAuthStore();
  const checkAuthStatus = useAuthStore(state => state.checkAuthStatus);
  const reset = useAuthStore(state => state.reset);
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);

  useEffect(() => {
    //        
    let mounted = true;
    
    const initAuth = async () => {
      if (mounted) {
        await checkAuthStatus();
      }
    };
    
    initAuth();

    //       
    const handleAuthFailure = () => {
      reset();
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('auth:failure', handleAuthFailure);
      
      //       
      const handleVisibilityChange = () => {
        if (document.visibilityState === 'visible' && isAuthenticated) {
          //   
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
  }, [checkAuthStatus, reset]); //     

  // Zustand      
  const contextValue: AuthContextType = {
    //  
    user: authStore.user,
    isLoading: authStore.isLoading,
    isAuthenticated: authStore.isAuthenticated,
    error: authStore.error,
    
    //   
    isLoginLoading: authStore.isLoginLoading,
    isSignupLoading: authStore.isSignupLoading,
    isPasswordResetLoading: authStore.isPasswordResetLoading,
    
    //  
    loginError: authStore.loginError,
    signupError: authStore.signupError,
    passwordResetError: authStore.passwordResetError,
    
    // 
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
    
    //     
    hasPermission: () => true, //  
    emailCheckResult: null, //  
    nicknameCheckResult: null, //  
    isEmailCheckLoading: false, //  
    isNicknameCheckLoading: false, //  
    
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
 *   
 *       
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 *     
 *      .
 */
export function useRequireAuth(): AuthContextType & { user: User } {
  const auth = useAuth();
  
  if (!auth.isAuthenticated || !auth.user) {
    throw new Error('This component requires authentication');
  }
  
  return auth as AuthContextType & { user: User };
}

/**
 *     
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