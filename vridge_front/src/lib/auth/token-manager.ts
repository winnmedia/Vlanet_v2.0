import type { AuthTokens } from '@/types';

/**
 * JWT    ()
 *  , ,   .
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
   *   
   */
  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }

  /**
   *    
   */
  private loadTokens(): void {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
      
      const expiryTime = localStorage.getItem('token_expiry');
      this.tokenExpiryTime = expiryTime ? parseInt(expiryTime) : null;

      //      
      if (this.tokenExpiryTime) {
        this.setupTokenRefresh();
      }
    }
  }

  /**
   *    
   */
  public setTokens(tokens: AuthTokens): void {
    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;
    
    // JWT    15 
    this.tokenExpiryTime = Date.now() + (15 * 60 * 1000);

    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('token_expiry', this.tokenExpiryTime.toString());
    }

    //    
    this.setupTokenRefresh();
  }

  /**
   *    (   )
   */
  public getAccessToken(): string | null {
    //    (1   )
    if (this.tokenExpiryTime && Date.now() > this.tokenExpiryTime - 60000) {
      this.refreshAccessToken();
    }
    return this.accessToken;
  }

  /**
   *   
   */
  public getRefreshToken(): string | null {
    return this.refreshToken;
  }

  /**
   *   
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
   *   
   */
  public isAuthenticated(): boolean {
    return !!this.accessToken && (!this.tokenExpiryTime || Date.now() < this.tokenExpiryTime);
  }

  /**
   *     ()
   */
  public getTimeUntilExpiry(): number {
    if (!this.tokenExpiryTime) return 0;
    return Math.max(0, this.tokenExpiryTime - Date.now());
  }

  /**
   *    
   */
  private setupTokenRefresh(): void {
    if (!this.tokenExpiryTime || !this.refreshToken) return;

    //   
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
    }

    //  2   ( 1 )
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
   *   
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
        
        //     (  )
        this.accessToken = data.access;
        this.tokenExpiryTime = Date.now() + (15 * 60 * 1000);

        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', data.access);
          localStorage.setItem('token_expiry', this.tokenExpiryTime.toString());
        }

        //   
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
   *   
   */
  private handleAuthFailure(): void {
    this.clearTokens();
    
    //    (    )
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('auth:failure');
      window.dispatchEvent(event);
      
      //    (,     )
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
  }

  /**
   *   
   */
  public validateTokenFormat(token: string): boolean {
    if (!token) return false;
    
    // JWT   (3  , base64 )
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      // Header Payload  
      JSON.parse(atob(parts[0]));
      JSON.parse(atob(parts[1]));
      return true;
    } catch {
      return false;
    }
  }

  /**
   * JWT   
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
   *   ID 
   */
  public getUserIdFromToken(): number | null {
    if (!this.accessToken) return null;
    
    const payload = this.decodeToken(this.accessToken);
    return payload?.user_id || null;
  }

  /**
   *    
   */
  public getTokenExpiry(): Date | null {
    if (!this.accessToken) return null;
    
    const payload = this.decodeToken(this.accessToken);
    return payload?.exp ? new Date(payload.exp * 1000) : null;
  }
}

//   export
export const tokenManager = TokenManager.getInstance();