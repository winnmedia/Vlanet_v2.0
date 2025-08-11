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
 * VideoPlanet API   
 * JWT  ,   ,    
 *   HTTP .
 */
export class APIClient {
  private baseURL: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;

  constructor(config?: APIClientConfig) {
    //  Next.js rewrites ,   Railway URL 
    this.baseURL = config?.baseURL || 
      process.env.NEXT_PUBLIC_API_URL || 
      (process.env.NODE_ENV === 'production' ? '' : 'https://videoplanet.up.railway.app');
    console.log('[APIClient] baseURL:', this.baseURL);
    this.timeout = config?.timeout || 30000;
    this.retryAttempts = config?.retryAttempts || 3;
    this.retryDelay = config?.retryDelay || 1000;
  }

  /**
   *  HTTP  
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
      console.log('[APIClient]   ');
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
        console.log(`[APIClient]  : ${response.status}`);
        return this.handleErrorResponse(response);
      }

      const data = await response.json();
      console.log('[APIClient]  :', data);
      return { success: true, data };
    } catch (error) {
      console.error('[APIClient]  :', error);
      return this.handleNetworkError(error);
    }
  }

  /**
   *    fetch 
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
   * HTTP   
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

    // 401 Unauthorized -   
    if (response.status === 401) {
      await this.handleUnauthorized();
    }

    return { success: false, error };
  }

  /**
   *   
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
   * 401 Unauthorized     
   */
  private async handleUnauthorized(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    
    if (refreshToken) {
      const result = await this.refreshAccessToken(refreshToken);
      
      if (!result.success) {
        //     
        this.clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    } else {
      //       
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  }

  /**
   *   
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
   *  
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ========================================
  //   
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
  //  
  // ========================================

  /**
   *  
   */
  public setTokens(tokens: AuthTokens): void {
    console.log('[APIClient]  :', tokens);
    if (tokens.access) {
      this.setAccessToken(tokens.access);
    }
    if (tokens.refresh) {
      this.setRefreshToken(tokens.refresh);
    }
  }

  /**
   * GET 
   */
  public async get<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('GET', endpoint, options);
  }

  /**
   * POST 
   */
  public async post<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('POST', endpoint, { ...options, body });
  }

  /**
   * PUT 
   */
  public async put<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('PUT', endpoint, { ...options, body });
  }

  /**
   * DELETE 
   */
  public async delete<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('DELETE', endpoint, options);
  }

  /**
   * PATCH 
   */
  public async patch<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('PATCH', endpoint, { ...options, body });
  }
}

//   export
export const apiClient = new APIClient();