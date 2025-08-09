import type { AuthTokens } from '@/types';

/**
 * JWT 토큰 관리 클래스 (싱글톤)
 * 토큰의 저장, 검증, 자동 갱신을 담당합니다.
 */
export class TokenManager {
  private static instance: TokenManager;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiryTime: number | null = null;
  private refreshTimeout: NodeJS.Timeout | null = null;

  private constructor() {
    this.loadTokens();
  }

  /**
   * 싱글톤 인스턴스 반환
   */
  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }

  /**
   * 로컬 스토리지에서 토큰 로드
   */
  private loadTokens(): void {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
      
      const expiryTime = localStorage.getItem('token_expiry');
      this.tokenExpiryTime = expiryTime ? parseInt(expiryTime) : null;

      // 기존 토큰이 있으면 자동 갱신 설정
      if (this.tokenExpiryTime) {
        this.setupTokenRefresh();
      }
    }
  }

  /**
   * 토큰 설정 및 저장
   */
  public setTokens(tokens: AuthTokens): void {
    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;
    
    // JWT 액세스 토큰은 일반적으로 15분 유효
    this.tokenExpiryTime = Date.now() + (15 * 60 * 1000);

    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('token_expiry', this.tokenExpiryTime.toString());
    }

    // 자동 토큰 갱신 설정
    this.setupTokenRefresh();
  }

  /**
   * 액세스 토큰 반환 (만료 시 자동 갱신)
   */
  public getAccessToken(): string | null {
    // 토큰 만료 확인 (1분 여유 시간 포함)
    if (this.tokenExpiryTime && Date.now() > this.tokenExpiryTime - 60000) {
      this.refreshAccessToken();
    }
    return this.accessToken;
  }

  /**
   * 리프레시 토큰 반환
   */
  public getRefreshToken(): string | null {
    return this.refreshToken;
  }

  /**
   * 모든 토큰 삭제
   */
  public clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiryTime = null;

    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
      this.refreshTimeout = null;
    }

    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token_expiry');
    }
  }

  /**
   * 인증 상태 확인
   */
  public isAuthenticated(): boolean {
    return !!this.accessToken && (!this.tokenExpiryTime || Date.now() < this.tokenExpiryTime);
  }

  /**
   * 토큰 만료까지 남은 시간 (밀리초)
   */
  public getTimeUntilExpiry(): number {
    if (!this.tokenExpiryTime) return 0;
    return Math.max(0, this.tokenExpiryTime - Date.now());
  }

  /**
   * 자동 토큰 갱신 설정
   */
  private setupTokenRefresh(): void {
    if (!this.tokenExpiryTime || !this.refreshToken) return;

    // 기존 타이머 클리어
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
    }

    // 만료 2분 전에 갱신 (최소 1분 전)
    const refreshTime = Math.max(
      this.tokenExpiryTime - Date.now() - (2 * 60 * 1000), 
      60 * 1000
    );
    
    if (refreshTime > 0) {
      this.refreshTimeout = setTimeout(() => {
        this.refreshAccessToken();
      }, refreshTime);
    }
  }

  /**
   * 액세스 토큰 갱신
   */
  private async refreshAccessToken(): Promise<void> {
    if (!this.refreshToken) {
      this.handleAuthFailure();
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // 새 액세스 토큰만 업데이트 (리프레시 토큰은 그대로)
        this.accessToken = data.access;
        this.tokenExpiryTime = Date.now() + (15 * 60 * 1000);

        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('token_expiry', this.tokenExpiryTime.toString());
        }

        // 다음 갱신 예약
        this.setupTokenRefresh();
        
        console.log('Token refreshed successfully');
      } else {
        this.handleAuthFailure();
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.handleAuthFailure();
    }
  }

  /**
   * 인증 실패 처리
   */
  private handleAuthFailure(): void {
    this.clearTokens();
    
    // 커스텀 이벤트 발생 (인증 실패를 다른 컴포넌트에 알림)
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('auth:failure');
      window.dispatchEvent(event);
      
      // 로그인 페이지로 리다이렉트 (단, 이미 로그인 페이지가 아닌 경우에만)
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
  }

  /**
   * 토큰 유효성 검증
   */
  public validateTokenFormat(token: string): boolean {
    if (!token) return false;
    
    // JWT 형식 검증 (3개 부분으로 구성, base64 인코딩)
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      // Header와 Payload 디코딩 시도
      JSON.parse(atob(parts[0]));
      JSON.parse(atob(parts[1]));
      return true;
    } catch {
      return false;
    }
  }

  /**
   * JWT 토큰 페이로드 디코딩
   */
  public decodeToken(token: string): any {
    try {
      const payload = token.split('.')[1];
      return JSON.parse(atob(payload));
    } catch {
      return null;
    }
  }

  /**
   * 토큰에서 사용자 ID 추출
   */
  public getUserIdFromToken(): number | null {
    if (!this.accessToken) return null;
    
    const payload = this.decodeToken(this.accessToken);
    return payload?.user_id || null;
  }

  /**
   * 토큰 만료 시간 추출
   */
  public getTokenExpiry(): Date | null {
    if (!this.accessToken) return null;
    
    const payload = this.decodeToken(this.accessToken);
    return payload?.exp ? new Date(payload.exp * 1000) : null;
  }
}

// 싱글톤 인스턴스 export
export const tokenManager = TokenManager.getInstance();