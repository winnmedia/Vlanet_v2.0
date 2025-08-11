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
 *   API  
 * , ,        .
 */
export class AuthService extends APIClient {
  
  // ========================================
  //   
  // ========================================

  /**
   * Enhanced Login with improved error handling and response parsing
   */
  async login(credentials: LoginRequest): Promise<APIResponse<LoginResponse>> {
    console.log('[AuthService] Login attempt:', { email: credentials.email });
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const startTime = Date.now();
      
      const response = await fetch(`${apiUrl}/api/users/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include', // Include cookies for CORS
        body: JSON.stringify(credentials),
      });

      const responseTime = Date.now() - startTime;
      console.log(`[AuthService] API Response time: ${responseTime}ms`);

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error('[AuthService] Failed to parse response JSON:', parseError);
        return {
          success: false,
          error: {
            status: response.status,
            message: 'Invalid server response format',
            code: 'PARSE_ERROR'
          }
        };
      }

      console.log('[AuthService] Response data:', {
        success: data.success,
        status: response.status,
        hasData: !!data.data,
        requestId: data.request_id,
        responseTime: data.performance?.response_time_ms
      });

      if (response.ok && data.success) {
        // Enhanced token handling with validation
        const tokenData = data.data;
        
        if (tokenData.access_token || tokenData.access) {
          const accessToken = tokenData.access_token || tokenData.access;
          const refreshToken = tokenData.refresh_token || tokenData.refresh;
          const vrideSession = tokenData.vridge_session;
          
          // Store tokens
          localStorage.setItem('access_token', accessToken);
          if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
          }
          if (vrideSession) {
            localStorage.setItem('vridge_session', vrideSession);
          }
          
          // Store token expiry
          if (tokenData.expires_in) {
            const expiryTime = Date.now() + (tokenData.expires_in * 1000);
            localStorage.setItem('token_expiry', expiryTime.toString());
          }
          
          // Store user data
          if (tokenData.user) {
            localStorage.setItem('user_data', JSON.stringify(tokenData.user));
          }
          
          console.log('[AuthService] Login successful:', {
            userId: tokenData.user?.id,
            email: tokenData.user?.email,
            expiresIn: tokenData.expires_in
          });
        }
        
        return { success: true, data: tokenData };
        
      } else {
        // Handle API error response
        const errorInfo = data.error || {};
        console.error('[AuthService] Login failed:', {
          status: response.status,
          code: errorInfo.code,
          message: errorInfo.message,
          requestId: data.request_id
        });
        
        return { 
          success: false, 
          error: {
            status: response.status,
            message: errorInfo.message || data.message || 'Login failed',
            code: errorInfo.code || 'LOGIN_FAILED',
            details: errorInfo.details,
            requestId: data.request_id
          }
        };
      }
    } catch (error) {
      console.error('[AuthService] Network/unexpected error:', error);
      
      // Handle specific error types
      let errorMessage = 'A network error occurred. Please check your connection and try again.';
      let errorCode = 'NETWORK_ERROR';
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage = 'Unable to connect to server. Please check your internet connection.';
        errorCode = 'CONNECTION_ERROR';
      } else if (error instanceof Error) {
        errorMessage = `Request failed: ${error.message}`;
        errorCode = 'REQUEST_ERROR';
      }
      
      return {
        success: false,
        error: {
          status: 0,
          message: errorMessage,
          code: errorCode
        }
      };
    }
  }

  /**
   *  
   */
  async signup(data: SignupRequest): Promise<APIResponse<SignupResponse>> {
    const response = await this.post<SignupResponse>('/api/auth/signup/', data, {
      skipAuth: true,
    });

    if (response.success && response.data) {
      //   
      this.setTokens(response.data.tokens);
    }

    return response;
  }

  /**
   * 
   */
  async logout(): Promise<void> {
    try {
      //    ()
      await this.post('/api/users/logout/', {});
    } catch (error) {
      //      
      console.warn('Server logout failed, but local tokens will be cleared');
    } finally {
      //   
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token_expiry');
      }
    }
  }

  /**
   *    
   */
  async getCurrentUser(): Promise<APIResponse<User>> {
    return this.get<User>('/api/users/me/');
  }

  /**
   *   
   */
  async updateProfile(data: Partial<User>): Promise<APIResponse<User>> {
    return this.patch<User>('/api/users/me/', data);
  }

  /**
   *  
   */
  async changePassword(data: {
    current_password: string;
    new_password: string;
  }): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/users/change-password/', data);
  }

  // ========================================
  //     
  // ========================================

  /**
   *   
   */
  async checkEmailAvailability(email: string): Promise<APIResponse<{ available: boolean; message: string }>> {
    return this.post('/api/auth/check-email/', { email }, { skipAuth: true });
  }

  /**
   *   
   */
  async checkNicknameAvailability(nickname: string): Promise<APIResponse<{ available: boolean; message: string }>> {
    return this.post('/api/auth/check-nickname/', { nickname }, { skipAuth: true });
  }

  // ========================================
  //  
  // ========================================

  /**
   *   
   */
  async requestPasswordReset(email: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/password-reset-request/', { email }, {
      skipAuth: true,
    });
  }

  /**
   *    
   */
  async verifyPasswordResetToken(token: string): Promise<APIResponse<{ valid: boolean }>> {
    return this.post<{ valid: boolean }>('/api/auth/verify-reset-token/', { token }, {
      skipAuth: true,
    });
  }

  /**
   *   
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
  //  
  // ========================================

  /**
   *   
   */
  async requestEmailVerification(): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/verify-email-request/');
  }

  /**
   *   
   */
  async verifyEmail(token: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/verify-email/', { token }, {
      skipAuth: true,
    });
  }

  // ========================================
  //  
  // ========================================

  /**
   * Google  URL 
   */
  async getGoogleLoginUrl(): Promise<APIResponse<{ auth_url: string; state: string }>> {
    return this.get<{ auth_url: string; state: string }>('/api/auth/google/login/', {
      skipAuth: true,
    });
  }

  /**
   * Google   
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
   * Kakao  URL 
   */
  async getKakaoLoginUrl(): Promise<APIResponse<{ auth_url: string; state: string }>> {
    return this.get<{ auth_url: string; state: string }>('/api/auth/kakao/login/', {
      skipAuth: true,
    });
  }

  /**
   * Kakao   
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
  //  
  // ========================================

  /**
   *  
   */
  async deactivateAccount(): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/deactivate/');
  }

  /**
   *   
   */
  async requestAccountDeletion(): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/delete-account-request/');
  }

  /**
   *   
   */
  async deleteAccount(password: string): Promise<APIResponse<{ message: string }>> {
    return this.post<{ message: string }>('/api/auth/delete-account/', { password });
  }

  // ========================================
  //   
  // ========================================

  /**
   *   
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
   *   
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
   *   
   */
  async terminateSession(sessionId: string): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/auth/sessions/${sessionId}/`);
  }

  /**
   *    
   */
  async terminateAllOtherSessions(): Promise<APIResponse<{ message: string, terminated_count: number }>> {
    return this.post<{ message: string, terminated_count: number }>('/api/auth/terminate-all-sessions/');
  }

  // ========================================
  //  
  // ========================================

  /**
   *    
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    
    const token = localStorage.getItem('access_token');
    const expiry = localStorage.getItem('token_expiry');
    
    if (!token || !expiry) return false;
    
    return Date.now() < parseInt(expiry);
  }

  /**
   *   ID 
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
   *     ()
   */
  getTimeUntilTokenExpiry(): number {
    if (typeof window === 'undefined') return 0;
    
    const expiry = localStorage.getItem('token_expiry');
    if (!expiry) return 0;
    
    return Math.max(0, parseInt(expiry) - Date.now());
  }
}

//   export
export const authService = new AuthService();