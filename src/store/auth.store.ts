import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/lib/api/auth.service';
import { tokenManager } from '@/lib/auth/token-manager';
import type { User, LoginRequest, SignupRequest, APIError } from '@/types';

// ========================================
// 상태 인터페이스
// ========================================

interface AuthState {
  // 상태
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // 로그인 관련
  isLoginLoading: boolean;
  loginError: string | null;
  
  // 회원가입 관련
  isSignupLoading: boolean;
  signupError: string | null;
  
  // 비밀번호 재설정 관련
  isPasswordResetLoading: boolean;
  passwordResetError: string | null;
  passwordResetEmailSent: boolean;
  
  // 프로필 업데이트 관련
  isProfileUpdateLoading: boolean;
  profileUpdateError: string | null;
  
  // 이메일/닉네임 중복 확인
  emailCheckResult: { available: boolean; message: string } | null;
  nicknameCheckResult: { available: boolean; message: string } | null;
  isEmailCheckLoading: boolean;
  isNicknameCheckLoading: boolean;
}

interface AuthActions {
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
  
  // 소셜 로그인
  loginWithGoogle: () => Promise<void>;
  loginWithKakao: () => Promise<void>;
  handleSocialLoginCallback: (provider: 'google' | 'kakao', code: string, state: string) => Promise<boolean>;
  
  // 에러 관리
  clearError: () => void;
  clearLoginError: () => void;
  clearSignupError: () => void;
  clearPasswordResetError: () => void;
  clearProfileUpdateError: () => void;
  
  // 상태 초기화
  reset: () => void;
}

type AuthStore = AuthState & AuthActions;

// ========================================
// 초기 상태
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
};

// ========================================
// 유틸리티 함수
// ========================================

/**
 * API 에러에서 사용자 친화적 메시지 추출
 */
const getErrorMessage = (error: APIError | Error | unknown): string => {
  if (typeof error === 'object' && error !== null) {
    if ('message' in error) {
      return (error as APIError).message;
    }
    if ('details' in error) {
      const details = (error as APIError).details;
      if (details && typeof details === 'object') {
        // Django REST Framework 에러 형식 처리
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
  
  return '알 수 없는 오류가 발생했습니다.';
};

// ========================================
// Zustand 스토어 생성
// ========================================

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // ========================================
      // 기본 인증 액션
      // ========================================

      /**
       * 로그인
       */
      login: async (credentials: LoginRequest): Promise<boolean> => {
        console.log('[AuthStore] 로그인 시작:', { email: credentials.email });
        set({ isLoginLoading: true, loginError: null });

        try {
          const response = await authService.login(credentials);
          console.log('[AuthStore] 로그인 응답 받음:', response);
          
          if (response.success && response.data) {
            // 백엔드 응답 형식: { vridge_session, access, refresh, user }
            const userData = response.data.user || response.data;
            console.log('[AuthStore] 사용자 데이터:', userData);
            
            set({
              user: userData,
              isAuthenticated: true,
              isLoginLoading: false,
              loginError: null,
            });
            console.log('[AuthStore] 로그인 성공');
            return true;
          } else {
            const errorMsg = getErrorMessage(response.error);
            console.log('[AuthStore] 로그인 실패:', errorMsg);
            set({
              isLoginLoading: false,
              loginError: errorMsg,
            });
            return false;
          }
        } catch (error) {
          const errorMsg = getErrorMessage(error);
          console.error('[AuthStore] 로그인 에러:', error);
          set({
            isLoginLoading: false,
            loginError: errorMsg,
          });
          return false;
        }
      },

      /**
       * 회원가입
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
       * 로그아웃
       */
      logout: async (): Promise<void> => {
        try {
          await authService.logout();
        } catch (error) {
          console.warn('Logout request failed:', error);
        } finally {
          // 토큰 매니저 클리어
          tokenManager.clearTokens();
          
          // 상태 초기화
          set({
            ...initialState,
          });
        }
      },

      /**
       * 사용자 정보 새로고침
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
       * 인증 상태 확인
       */
      checkAuthStatus: async (): Promise<void> => {
        // 이미 체크 중이면 중복 실행 방지
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
              // 토큰은 있지만 사용자 정보 조회 실패 - 토큰 클리어
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
      // 비밀번호 관리
      // ========================================

      /**
       * 비밀번호 재설정 요청
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
       * 비밀번호 재설정 실행
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
       * 비밀번호 변경
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
      // 프로필 관리
      // ========================================

      /**
       * 프로필 업데이트
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
      // 유효성 검사
      // ========================================

      /**
       * 이메일 중복 확인
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
       * 닉네임 중복 확인
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

      // ========================================
      // 소셜 로그인
      // ========================================

      /**
       * Google 로그인
       */
      loginWithGoogle: async (): Promise<void> => {
        try {
          const response = await authService.getGoogleLoginUrl();
          
          if (response.success && response.data) {
            // 상태 값을 세션 스토리지에 저장
            sessionStorage.setItem('oauth_state', response.data.state);
            
            // Google 로그인 페이지로 리다이렉트
            window.location.href = response.data.auth_url;
          }
        } catch (error) {
          set({ error: getErrorMessage(error) });
        }
      },

      /**
       * Kakao 로그인
       */
      loginWithKakao: async (): Promise<void> => {
        try {
          const response = await authService.getKakaoLoginUrl();
          
          if (response.success && response.data) {
            // 상태 값을 세션 스토리지에 저장
            sessionStorage.setItem('oauth_state', response.data.state);
            
            // Kakao 로그인 페이지로 리다이렉트
            window.location.href = response.data.auth_url;
          }
        } catch (error) {
          set({ error: getErrorMessage(error) });
        }
      },

      /**
       * 소셜 로그인 콜백 처리
       */
      handleSocialLoginCallback: async (
        provider: 'google' | 'kakao', 
        code: string, 
        state: string
      ): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          // 상태 검증
          const savedState = sessionStorage.getItem('oauth_state');
          if (savedState !== state) {
            set({
              isLoading: false,
              error: '잘못된 요청입니다. 다시 시도해주세요.',
            });
            return false;
          }

          // 콜백 처리
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
            
            // 상태 값 정리
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
      // 에러 관리
      // ========================================

      clearError: () => set({ error: null }),
      clearLoginError: () => set({ loginError: null }),
      clearSignupError: () => set({ signupError: null }),
      clearPasswordResetError: () => set({ passwordResetError: null, passwordResetEmailSent: false }),
      clearProfileUpdateError: () => set({ profileUpdateError: null }),

      // ========================================
      // 상태 초기화
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