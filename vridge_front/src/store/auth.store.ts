import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/lib/api/auth.service';
import { tokenManager } from '@/lib/auth/token-manager';
import type { User, LoginRequest, SignupRequest, APIError } from '@/types';

// ========================================
//  
// ========================================

interface AuthState {
  // 
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  //  
  isLoginLoading: boolean;
  loginError: string | null;
  
  //  
  isSignupLoading: boolean;
  signupError: string | null;
  
  //   
  isPasswordResetLoading: boolean;
  passwordResetError: string | null;
  passwordResetEmailSent: boolean;
  
  //   
  isProfileUpdateLoading: boolean;
  profileUpdateError: string | null;
  
  // /  
  emailCheckResult: { available: boolean; message: string } | null;
  nicknameCheckResult: { available: boolean; message: string } | null;
  isEmailCheckLoading: boolean;
  isNicknameCheckLoading: boolean;
  
  // 이메일 인증 상태 관리
  emailVerificationStatus: 'none' | 'sent' | 'verified' | 'failed';
  isEmailVerificationLoading: boolean;
  emailVerificationError: string | null;
  verificationCodeSentAt: number | null;
  isResendLoading: boolean;
}

interface AuthActions {
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
  
  // 중복 체크 및 이메일 인증
  checkEmailAvailability: (email: string) => Promise<void>;
  checkNicknameAvailability: (nickname: string) => Promise<void>;
  verifyEmailCode: (email: string, code: string) => Promise<boolean>;
  resendVerificationCode: (email: string) => Promise<boolean>;
  
  //  
  loginWithGoogle: () => Promise<void>;
  loginWithKakao: () => Promise<void>;
  handleSocialLoginCallback: (provider: 'google' | 'kakao', code: string, state: string) => Promise<boolean>;
  
  //  
  clearError: () => void;
  clearLoginError: () => void;
  clearSignupError: () => void;
  clearPasswordResetError: () => void;
  clearProfileUpdateError: () => void;
  
  //  
  reset: () => void;
}

type AuthStore = AuthState & AuthActions;

// ========================================
//  
// ========================================

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  isLoginLoading: false,
  loginError: null,
  
  isSignupLoading: false,
  signupError: null,
  
  isPasswordResetLoading: false,
  passwordResetError: null,
  passwordResetEmailSent: false,
  
  isProfileUpdateLoading: false,
  profileUpdateError: null,
  
  emailCheckResult: null,
  nicknameCheckResult: null,
  isEmailCheckLoading: false,
  isNicknameCheckLoading: false,
  
  emailVerificationStatus: 'none',
  isEmailVerificationLoading: false,
  emailVerificationError: null,
  verificationCodeSentAt: null,
  isResendLoading: false,
};

// ========================================
//  
// ========================================

/**
 * API     
 */
const getErrorMessage = (error: APIError | Error | unknown): string => {
  if (typeof error === 'object' && error !== null) {
    if ('message' in error) {
      return (error as APIError).message;
    }
    if ('details' in error) {
      const details = (error as APIError).details;
      if (details && typeof details === 'object') {
        // Django REST Framework   
        const firstError = Object.values(details)[0];
        if (Array.isArray(firstError) && firstError.length > 0) {
          return firstError[0];
        }
      }
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return '    .';
};

// ========================================
// Zustand  
// ========================================

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // ========================================
      //   
      // ========================================

      /**
       * 
       */
      login: async (credentials: LoginRequest): Promise<boolean> => {
        console.log('[AuthStore]  :', { email: credentials.email });
        set({ isLoginLoading: true, loginError: null });

        try {
          const response = await authService.login(credentials);
          console.log('[AuthStore]   :', response);
          
          if (response.success && response.data) {
            //   : { vridge_session, access, refresh, user }
            const userData = response.data.user || response.data;
            console.log('[AuthStore]  :', userData);
            
            set({
              user: userData,
              isAuthenticated: true,
              isLoginLoading: false,
              loginError: null,
            });
            console.log('[AuthStore]  ');
            return true;
          } else {
            const errorMsg = getErrorMessage(response.error);
            console.log('[AuthStore]  :', errorMsg);
            set({
              isLoginLoading: false,
              loginError: errorMsg,
            });
            return false;
          }
        } catch (error) {
          const errorMsg = getErrorMessage(error);
          console.error('[AuthStore]  :', error);
          set({
            isLoginLoading: false,
            loginError: errorMsg,
          });
          return false;
        }
      },

      /**
       * 
       */
      signup: async (data: SignupRequest): Promise<boolean> => {
        set({ isSignupLoading: true, signupError: null });

        try {
          const response = await authService.signup(data);
          
          if (response.success && response.data) {
            set({
              user: response.data.user,
              isAuthenticated: true,
              isSignupLoading: false,
              signupError: null,
            });
            return true;
          } else {
            set({
              isSignupLoading: false,
              signupError: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isSignupLoading: false,
            signupError: getErrorMessage(error),
          });
          return false;
        }
      },

      /**
       * 
       */
      logout: async (): Promise<void> => {
        try {
          await authService.logout();
        } catch (error) {
          console.warn('Logout request failed:', error);
        } finally {
          //   
          tokenManager.clearTokens();
          
          //  
          set({
            ...initialState,
          });
        }
      },

      /**
       *   
       */
      refreshUser: async (): Promise<void> => {
        if (!get().isAuthenticated) return;

        set({ isLoading: true, error: null });

        try {
          const response = await authService.getCurrentUser();
          
          if (response.success && response.data) {
            set({
              user: response.data,
              isLoading: false,
              error: null,
            });
          } else {
            set({
              isLoading: false,
              error: getErrorMessage(response.error),
            });
          }
        } catch (error) {
          set({
            isLoading: false,
            error: getErrorMessage(error),
          });
        }
      },

      /**
       *   
       */
      checkAuthStatus: async (): Promise<void> => {
        //      
        const state = get();
        if (state.isLoading) {
          return;
        }

        set({ isLoading: true });

        if (tokenManager.isAuthenticated()) {
          try {
            const response = await authService.getCurrentUser();
            
            if (response.success && response.data) {
              set({
                user: response.data,
                isAuthenticated: true,
                isLoading: false,
                error: null,
              });
            } else {
              //       -  
              tokenManager.clearTokens();
              set({
                ...initialState,
                isLoading: false,
              });
            }
          } catch (error) {
            tokenManager.clearTokens();
            set({
              ...initialState,
              isLoading: false,
              error: getErrorMessage(error),
            });
          }
        } else {
          set({
            ...initialState,
            isLoading: false,
          });
        }
      },

      // ========================================
      //  
      // ========================================

      /**
       *   
       */
      requestPasswordReset: async (email: string): Promise<boolean> => {
        set({ isPasswordResetLoading: true, passwordResetError: null });

        try {
          const response = await authService.requestPasswordReset(email);
          
          if (response.success) {
            set({
              isPasswordResetLoading: false,
              passwordResetError: null,
              passwordResetEmailSent: true,
            });
            return true;
          } else {
            set({
              isPasswordResetLoading: false,
              passwordResetError: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isPasswordResetLoading: false,
            passwordResetError: getErrorMessage(error),
          });
          return false;
        }
      },

      /**
       *   
       */
      resetPassword: async (token: string, newPassword: string): Promise<boolean> => {
        set({ isPasswordResetLoading: true, passwordResetError: null });

        try {
          const response = await authService.resetPassword(token, newPassword);
          
          if (response.success) {
            set({
              isPasswordResetLoading: false,
              passwordResetError: null,
            });
            return true;
          } else {
            set({
              isPasswordResetLoading: false,
              passwordResetError: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isPasswordResetLoading: false,
            passwordResetError: getErrorMessage(error),
          });
          return false;
        }
      },

      /**
       *  
       */
      changePassword: async (currentPassword: string, newPassword: string): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          const response = await authService.changePassword({
            current_password: currentPassword,
            new_password: newPassword,
          });
          
          if (response.success) {
            set({
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              isLoading: false,
              error: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isLoading: false,
            error: getErrorMessage(error),
          });
          return false;
        }
      },

      // ========================================
      //  
      // ========================================

      /**
       *  
       */
      updateProfile: async (data: Partial<User>): Promise<boolean> => {
        set({ isProfileUpdateLoading: true, profileUpdateError: null });

        try {
          const response = await authService.updateProfile(data);
          
          if (response.success && response.data) {
            set({
              user: response.data,
              isProfileUpdateLoading: false,
              profileUpdateError: null,
            });
            return true;
          } else {
            set({
              isProfileUpdateLoading: false,
              profileUpdateError: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isProfileUpdateLoading: false,
            profileUpdateError: getErrorMessage(error),
          });
          return false;
        }
      },

      // ========================================
      //  
      // ========================================

      /**
       *   
       */
      checkEmailAvailability: async (email: string): Promise<void> => {
        set({ isEmailCheckLoading: true });

        try {
          const response = await authService.checkEmailAvailability(email);
          
          if (response.success && response.data) {
            set({
              emailCheckResult: response.data,
              isEmailCheckLoading: false,
            });
          } else {
            set({
              emailCheckResult: null,
              isEmailCheckLoading: false,
            });
          }
        } catch (error) {
          set({
            emailCheckResult: null,
            isEmailCheckLoading: false,
          });
        }
      },

      /**
       *   
       */
      checkNicknameAvailability: async (nickname: string): Promise<void> => {
        set({ isNicknameCheckLoading: true });

        try {
          const response = await authService.checkNicknameAvailability(nickname);
          
          if (response.success && response.data) {
            set({
              nicknameCheckResult: response.data,
              isNicknameCheckLoading: false,
            });
          } else {
            set({
              nicknameCheckResult: null,
              isNicknameCheckLoading: false,
            });
          }
        } catch (error) {
          set({
            nicknameCheckResult: null,
            isNicknameCheckLoading: false,
          });
        }
      },

      /**
       * 이메일 인증 코드 검증
       */
      verifyEmailCode: async (email: string, code: string): Promise<boolean> => {
        set({ isEmailVerificationLoading: true, emailVerificationError: null });

        try {
          const response = await authService.verifyEmailCode(email, code);
          
          if (response.success && response.data) {
            set({
              isEmailVerificationLoading: false,
              emailVerificationStatus: response.data.verified ? 'verified' : 'failed',
              emailVerificationError: response.data.verified ? null : response.data.message,
            });
            return response.data.verified;
          } else {
            set({
              isEmailVerificationLoading: false,
              emailVerificationStatus: 'failed',
              emailVerificationError: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isEmailVerificationLoading: false,
            emailVerificationStatus: 'failed',
            emailVerificationError: getErrorMessage(error),
          });
          return false;
        }
      },

      /**
       * 인증 코드 재발송
       */
      resendVerificationCode: async (email: string): Promise<boolean> => {
        set({ isResendLoading: true, emailVerificationError: null });

        try {
          const response = await authService.resendVerificationCode(email);
          
          if (response.success) {
            set({
              isResendLoading: false,
              emailVerificationStatus: 'sent',
              verificationCodeSentAt: Date.now(),
              emailVerificationError: null,
            });
            return true;
          } else {
            set({
              isResendLoading: false,
              emailVerificationError: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isResendLoading: false,
            emailVerificationError: getErrorMessage(error),
          });
          return false;
        }
      },

      // ========================================
      //  
      // ========================================

      /**
       * Google 
       */
      loginWithGoogle: async (): Promise<void> => {
        try {
          const response = await authService.getGoogleLoginUrl();
          
          if (response.success && response.data) {
            //     
            sessionStorage.setItem('oauth_state', response.data.state);
            
            // Google   
            window.location.href = response.data.auth_url;
          }
        } catch (error) {
          set({ error: getErrorMessage(error) });
        }
      },

      /**
       * Kakao 
       */
      loginWithKakao: async (): Promise<void> => {
        try {
          const response = await authService.getKakaoLoginUrl();
          
          if (response.success && response.data) {
            //     
            sessionStorage.setItem('oauth_state', response.data.state);
            
            // Kakao   
            window.location.href = response.data.auth_url;
          }
        } catch (error) {
          set({ error: getErrorMessage(error) });
        }
      },

      /**
       *    
       */
      handleSocialLoginCallback: async (
        provider: 'google' | 'kakao', 
        code: string, 
        state: string
      ): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          //  
          const savedState = sessionStorage.getItem('oauth_state');
          if (savedState !== state) {
            set({
              isLoading: false,
              error: ' .  .',
            });
            return false;
          }

          //  
          const response = provider === 'google' 
            ? await authService.handleGoogleCallback(code, state)
            : await authService.handleKakaoCallback(code, state);

          if (response.success && response.data) {
            set({
              user: response.data.user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            //   
            sessionStorage.removeItem('oauth_state');
            return true;
          } else {
            set({
              isLoading: false,
              error: getErrorMessage(response.error),
            });
            return false;
          }
        } catch (error) {
          set({
            isLoading: false,
            error: getErrorMessage(error),
          });
          return false;
        }
      },

      // ========================================
      //  
      // ========================================

      clearError: () => set({ error: null }),
      clearLoginError: () => set({ loginError: null }),
      clearSignupError: () => set({ signupError: null }),
      clearPasswordResetError: () => set({ passwordResetError: null, passwordResetEmailSent: false }),
      clearProfileUpdateError: () => set({ profileUpdateError: null }),

      // ========================================
      //  
      // ========================================

      reset: () => set({ ...initialState }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);