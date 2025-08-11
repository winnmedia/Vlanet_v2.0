import type { APIResponse, APIError, AuthTokens } from '@/types';

interface APIClientConfig {
  baseURL?: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
}

interface RequestOptions {
  headers?: HeadersInit;
  body?: any;
  skipAuth?: boolean;
}

/**
 * VideoPlanet API 클라이언트 베이스 클래스
 * JWT 토큰 관리, 자동 토큰 갱신, 재시도 로직 등을 포함한
 * 타입 안전한 HTTP 클라이언트입니다.
 */
export class APIClient {
  private baseURL: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;

  constructor(config?: APIClientConfig) {
    // 프로덕션에서는 Next.js rewrites 사용, 로컬에서는 직접 Railway URL 사용
    this.baseURL = config?.baseURL || 
      process.env.NEXT_PUBLIC_API_URL || 
      (process.env.NODE_ENV === 'production' ? '' : 'https://videoplanet.up.railway.app');
    console.log('[APIClient] baseURL:', this.baseURL);
    this.timeout = config?.timeout || 30000;
    this.retryAttempts = config?.retryAttempts || 3;
    this.retryDelay = config?.retryDelay || 1000;
  }

  /**
   * 기본 HTTP 요청 메서드
   */
  private async request<T>(
    method: string,
    endpoint: string,
    options?: RequestOptions
  ): Promise<APIResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getAccessToken();
    
    console.log(`[APIClient] ${method} ${endpoint}`);
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    if (token && !options?.skipAuth) {
      (headers as any)['Authorization'] = `Bearer ${token}`;
      console.log('[APIClient] 토큰 헤더 추가');
    }

    const config: RequestInit = {
      method,
      headers,
      body: options?.body ? JSON.stringify(options.body) : undefined,
      signal: AbortSignal.timeout(this.timeout),
    };

    try {
      const response = await this.fetchWithRetry(url, config);
      
      if (!response.ok) {
        console.log(`[APIClient] 에러 응답: ${response.status}`);
        return this.handleErrorResponse(response);
      }

      const data = await response.json();
      console.log('[APIClient] 성공 응답:', data);
      return { success: true, data };
    } catch (error) {
      console.error('[APIClient] 네트워크 에러:', error);
      return this.handleNetworkError(error);
    }
  }

  /**
   * 재시도 로직이 포함된 fetch 메서드
   */
  private async fetchWithRetry(
    url: string,
    config: RequestInit,
    attempt = 1
  ): Promise<Response> {
    try {
      return await fetch(url, config);
    } catch (error) {
      if (attempt < this.retryAttempts) {
        await this.delay(this.retryDelay * attempt);
        return this.fetchWithRetry(url, config, attempt + 1);
      }
      throw error;
    }
  }

  /**
   * HTTP 에러 응답 처리
   */
  private async handleErrorResponse(response: Response): Promise<APIResponse> {
    let error: APIError;
    
    try {
      const data = await response.json();
      error = {
        message: data.message || data.detail || 'An error occurred',
        code: response.status.toString(),
        details: data,
      };
    } catch {
      error = {
        message: `HTTP ${response.status}: ${response.statusText}`,
        code: response.status.toString(),
      };
    }

    // 401 Unauthorized - 토큰 갱신 시도
    if (response.status === 401) {
      await this.handleUnauthorized();
    }

    return { success: false, error };
  }

  /**
   * 네트워크 에러 처리
   */
  private handleNetworkError(error: any): APIResponse {
    return {
      success: false,
      error: {
        message: error.message || 'Network error occurred',
        code: 'NETWORK_ERROR',
      },
    };
  }

  /**
   * 401 Unauthorized 에러 처리 및 토큰 갱신
   */
  private async handleUnauthorized(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    
    if (refreshToken) {
      const result = await this.refreshAccessToken(refreshToken);
      
      if (!result.success) {
        // 갱신 실패 시 로그아웃 처리
        this.clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    } else {
      // 리프레시 토큰이 없을 경우 로그인 페이지로 리다이렉트
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  }

  /**
   * 액세스 토큰 갱신
   */
  private async refreshAccessToken(refreshToken: string): Promise<APIResponse<AuthTokens>> {
    try {
      const response = await fetch(`${this.baseURL}/api/users/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.setAccessToken(data.access);
        return { success: true, data };
      }

      return { success: false, error: { message: 'Token refresh failed' } };
    } catch (error) {
      return { success: false, error: { message: 'Token refresh failed' } };
    }
  }

  /**
   * 딜레이 유틸리티
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ========================================
  // 토큰 관리 메서드
  // ========================================

  private getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  private getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  }

  private setAccessToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private setRefreshToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token);
    }
  }

  private clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  // ========================================
  // 공개 메서드
  // ========================================

  /**
   * 토큰 설정
   */
  public setTokens(tokens: AuthTokens): void {
    console.log('[APIClient] 토큰 설정:', tokens);
    if (tokens.access) {
      this.setAccessToken(tokens.access);
    }
    if (tokens.refresh) {
      this.setRefreshToken(tokens.refresh);
    }
  }

  /**
   * GET 요청
   */
  public async get<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('GET', endpoint, options);
  }

  /**
   * POST 요청
   */
  public async post<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('POST', endpoint, { ...options, body });
  }

  /**
   * PUT 요청
   */
  public async put<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('PUT', endpoint, { ...options, body });
  }

  /**
   * DELETE 요청
   */
  public async delete<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('DELETE', endpoint, options);
  }

  /**
   * PATCH 요청
   */
  public async patch<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('PATCH', endpoint, { ...options, body });
  }
}

// 싱글톤 인스턴스 export
export const apiClient = new APIClient();