import { APIClient } from './base';
import type { 
  APIResponse, 
  User, 
  LoginRequest, 
  LoginResponse, 
  SignupRequest, 
  SignupResponse,
  PaginatedResponse
} from '@/types';

/**
 * 인증 관련 API 서비스 클래스
 * 로그인, 회원가입, 사용자 정보 관리 등의 인증 관련 기능을 제공합니다.
 */
export class AuthService extends APIClient {
  
  // ========================================
  // 인증 관련 메서드
  // ========================================

  /**
   * 사용자 로그인
   */
  async login(credentials: LoginRequest): Promise<APIResponse<LoginResponse>> {
    console.log('[AuthService] 로그인 시도:', { email: credentials.email });
    
    try {
      // 직접 fetch 사용하여 백엔드와 통신
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/api/users/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();
      console.log('[AuthService] 로그인 응답:', data);

      if (response.ok && data) {
        // 토큰 저장
        if (data.access) {
          localStorage.setItem('access_token', data.access);
        }
        if (data.refresh) {
          localStorage.setItem('refresh_token', data.refresh);
        }
        if (data.vridge_session) {
          localStorage.setItem('vridge_session', data.vridge_session);
        }
        
        return { success: true, data };
      } else {
        return { 
          success: false, 
          error: {
            status: response.status,
            message: data.message || '로그인에 실패했습니다.',
            code: 'LOGIN_FAILED'
          }
        };
      }
    } catch (error) {
      console.error('[AuthService] 로그인 오류:', error);
      return {
        success: false,
        error: {
          status: 0,
          message: '네트워크 오류가 발생했습니다.',
          code: 'NETWORK_ERROR'
        }
      };
    }

    // 이 부분은 이미 위에서 처리됨 (중복 코드 제거)
  }

  /**
   * 사용자 회원가입
   */
  async signup(data: SignupRequest): Promise<APIResponse<SignupResponse>> {
    const response = await this.post<SignupResponse>('/api/auth/signup/', data, {
      skipAuth: true,
    });

    if (response.success && response.data) {
      // 토큰 자동 저장
      this.setTokens(response.data.tokens);
    }

    return response;
  }

  /**
   * 로그아웃
   */
  async logout(): Promise<void> {
    try {
      // 서버에 로그아웃 요청 (선택사항)
      await this.post('/api/users/logout/', {});
    } catch (error) {
      // 로그아웃 요청 실패해도 로컬 토큰은 삭제
      console.warn('Server logout failed, but local tokens will be cleared');
    } finally {
      // 로컬 토큰 삭제
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token_expiry');
      }
    }
  }

  /**
   * 현재 사용자 정보 조회
   */
  async getCurrentUser(): Promise<APIResponse<User>> {
    return this.get<User>('/api/users/me/');
  }

  /**
   * 사용자 프로필 업데이트
   */
  async updateProfile(data: Partial<User>): Promise<APIResponse<User>> {
    return this.patch<User>('/api/users/me/', data);
  }

  /**
   * 비밀번호 변경
   */
  async changePassword(data: {
    current_password: string;
    new_password: string;
  }): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/users/change-password/', data);
  }

  // ========================================
  // 이메일 및 닉네임 중복 확인
  // ========================================

  /**
   * 이메일 중복 확인
   */
  async checkEmailAvailability(email: string): Promise<APIResponse<{ available: boolean; message: string }>> {
    return this.post('/api/auth/check-email/', { email }, { skipAuth: true });
  }

  /**
   * 닉네임 중복 확인
   */
  async checkNicknameAvailability(nickname: string): Promise<APIResponse<{ available: boolean; message: string }>> {
    return this.post('/api/auth/check-nickname/', { nickname }, { skipAuth: true });
  }

  // ========================================
  // 비밀번호 재설정
  // ========================================

  /**
   * 비밀번호 재설정 요청
   */
  async requestPasswordReset(email: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/password-reset-request/', { email }, {
      skipAuth: true,
    });
  }

  /**
   * 비밀번호 재설정 토큰 검증
   */
  async verifyPasswordResetToken(token: string): Promise<APIResponse<{ valid: boolean }>> {
    return this.post<{ valid: boolean }>('/api/auth/verify-reset-token/', { token }, {
      skipAuth: true,
    });
  }

  /**
   * 비밀번호 재설정 실행
   */
  async resetPassword(token: string, newPassword: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/password-reset/', {
      token,
      new_password: newPassword,
    }, {
      skipAuth: true,
    });
  }

  // ========================================
  // 이메일 검증
  // ========================================

  /**
   * 이메일 검증 요청
   */
  async requestEmailVerification(): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/verify-email-request/');
  }

  /**
   * 이메일 검증 실행
   */
  async verifyEmail(token: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/verify-email/', { token }, {
      skipAuth: true,
    });
  }

  // ========================================
  // 소셜 로그인
  // ========================================

  /**
   * Google 로그인 URL 생성
   */
  async getGoogleLoginUrl(): Promise<APIResponse<{ auth_url: string; state: string }>> {
    return this.get<{ auth_url: string; state: string }>('/api/auth/google/login/', {
      skipAuth: true,
    });
  }

  /**
   * Google 로그인 콜백 처리
   */
  async handleGoogleCallback(code: string, state: string): Promise<APIResponse<LoginResponse>> {
    const response = await this.post<LoginResponse>('/api/auth/google/callback/', {
      code,
      state,
    }, {
      skipAuth: true,
    });

    if (response.success && response.data) {
      this.setTokens(response.data.tokens);
    }

    return response;
  }

  /**
   * Kakao 로그인 URL 생성
   */
  async getKakaoLoginUrl(): Promise<APIResponse<{ auth_url: string; state: string }>> {
    return this.get<{ auth_url: string; state: string }>('/api/auth/kakao/login/', {
      skipAuth: true,
    });
  }

  /**
   * Kakao 로그인 콜백 처리
   */
  async handleKakaoCallback(code: string, state: string): Promise<APIResponse<LoginResponse>> {
    const response = await this.post<LoginResponse>('/api/auth/kakao/callback/', {
      code,
      state,
    }, {
      skipAuth: true,
    });

    if (response.success && response.data) {
      this.setTokens(response.data.tokens);
    }

    return response;
  }

  // ========================================
  // 계정 관리
  // ========================================

  /**
   * 계정 비활성화
   */
  async deactivateAccount(): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/deactivate/');
  }

  /**
   * 계정 삭제 요청
   */
  async requestAccountDeletion(): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/delete-account-request/');
  }

  /**
   * 계정 삭제 실행
   */
  async deleteAccount(password: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/delete-account/', { password });
  }

  // ========================================
  // 계정 활동 로그
  // ========================================

  /**
   * 로그인 히스토리 조회
   */
  async getLoginHistory(params?: {
    page?: number;
    page_size?: number;
  }): Promise<APIResponse<PaginatedResponse<{
    id: number;
    ip_address: string;
    user_agent: string;
    location?: string;
    login_time: string;
    success: boolean;
  }>>> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }

    const endpoint = `/api/auth/login-history/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.get(endpoint);
  }

  /**
   * 활성 세션 조회
   */
  async getActiveSessions(): Promise<APIResponse<{
    current_session: {
      id: string;
      ip_address: string;
      user_agent: string;
      last_activity: string;
    };
    other_sessions: Array<{
      id: string;
      ip_address: string;
      user_agent: string;
      last_activity: string;
    }>;
  }>> {
    return this.get('/api/auth/sessions/');
  }

  /**
   * 특정 세션 종료
   */
  async terminateSession(sessionId: string): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/auth/sessions/${sessionId}/`);
  }

  /**
   * 모든 다른 세션 종료
   */
  async terminateAllOtherSessions(): Promise<APIResponse<{ message: string, terminated_count: number }>> {
    return this.post<{ message: string, terminated_count: number }>('/api/auth/terminate-all-sessions/');
  }

  // ========================================
  // 헬퍼 메서드
  // ========================================

  /**
   * 현재 인증 상태 확인
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    
    const token = localStorage.getItem('access_token');
    const expiry = localStorage.getItem('token_expiry');
    
    if (!token || !expiry) return false;
    
    return Date.now() < parseInt(expiry);
  }

  /**
   * 토큰에서 사용자 ID 추출
   */
  getCurrentUserId(): number | null {
    if (typeof window === 'undefined') return null;
    
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.user_id || null;
    } catch {
      return null;
    }
  }

  /**
   * 토큰 만료까지 남은 시간 (밀리초)
   */
  getTimeUntilTokenExpiry(): number {
    if (typeof window === 'undefined') return 0;
    
    const expiry = localStorage.getItem('token_expiry');
    if (!expiry) return 0;
    
    return Math.max(0, parseInt(expiry) - Date.now());
  }
}

// 싱글톤 인스턴스 export
export const authService = new AuthService();