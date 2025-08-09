# VideoPlanet API Integration Guide

## 목차
1. [개요](#개요)
2. [API 엔드포인트 명세](#api-엔드포인트-명세)
3. [Request/Response 인터페이스](#requestresponse-인터페이스)
4. [API 클라이언트 구조](#api-클라이언트-구조)
5. [인증 토큰 관리 전략](#인증-토큰-관리-전략)
6. [에러 처리 패턴](#에러-처리-패턴)
7. [Mock 데이터 및 테스트 전략](#mock-데이터-및-테스트-전략)
8. [타입 안정성 보장 방안](#타입-안정성-보장-방안)

## 개요

### API 서버 정보
- **Base URL**: `https://videoplanet.up.railway.app`
- **API Version**: 1.0.0
- **Protocol**: HTTPS
- **Authentication**: JWT (JSON Web Token)
- **Content-Type**: `application/json`

### 주요 특징
- Django REST Framework 기반
- JWT 토큰 인증 (SimpleJWT)
- CORS 지원
- RESTful API 설계
- 표준 HTTP 상태 코드 사용

## API 엔드포인트 명세

### 1. 인증 API (Authentication)

#### 회원가입
```
POST /api/auth/signup/
```
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string",
    "nickname": "string",
    "phone": "string (optional)",
    "company": "string (optional)"
  }
  ```
- **Response**: 
  ```json
  {
    "user": {
      "id": "number",
      "email": "string",
      "nickname": "string"
    },
    "tokens": {
      "access": "string",
      "refresh": "string"
    }
  }
  ```

#### 로그인
```
POST /api/auth/login/
```
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "user": {
      "id": "number",
      "email": "string",
      "nickname": "string",
      "profile_image": "string | null"
    },
    "tokens": {
      "access": "string",
      "refresh": "string"
    }
  }
  ```

#### 토큰 갱신
```
POST /api/auth/refresh/
```
- **Request Body**:
  ```json
  {
    "refresh": "string"
  }
  ```
- **Response**:
  ```json
  {
    "access": "string"
  }
  ```

#### 사용자 정보 조회
```
GET /api/auth/me/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Response**:
  ```json
  {
    "id": "number",
    "email": "string",
    "nickname": "string",
    "profile_image": "string | null",
    "company": "string | null",
    "phone": "string | null",
    "created_at": "string",
    "email_verified": "boolean"
  }
  ```

#### 이메일 중복 확인
```
POST /api/auth/check-email/
```
- **Request Body**:
  ```json
  {
    "email": "string"
  }
  ```
- **Response**:
  ```json
  {
    "available": "boolean",
    "message": "string"
  }
  ```

#### 닉네임 중복 확인
```
POST /api/auth/check-nickname/
```
- **Request Body**:
  ```json
  {
    "nickname": "string"
  }
  ```
- **Response**:
  ```json
  {
    "available": "boolean",
    "message": "string"
  }
  ```

### 2. 프로젝트 API (Projects)

#### 프로젝트 목록 조회
```
GET /api/projects/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Query Parameters**:
  - `page`: number (default: 1)
  - `page_size`: number (default: 10)
  - `search`: string (optional)
  - `status`: string (optional: active | completed | archived)
- **Response**:
  ```json
  {
    "count": "number",
    "next": "string | null",
    "previous": "string | null",
    "results": [
      {
        "id": "number",
        "title": "string",
        "description": "string",
        "status": "string",
        "created_at": "string",
        "updated_at": "string",
        "owner": {
          "id": "number",
          "nickname": "string"
        },
        "members_count": "number",
        "thumbnail": "string | null"
      }
    ]
  }
  ```

#### 프로젝트 생성
```
POST /api/projects/create/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "start_date": "string (YYYY-MM-DD)",
    "end_date": "string (YYYY-MM-DD)",
    "status": "string (default: active)",
    "is_public": "boolean (default: false)"
  }
  ```
- **Response**:
  ```json
  {
    "id": "number",
    "title": "string",
    "description": "string",
    "start_date": "string",
    "end_date": "string",
    "status": "string",
    "is_public": "boolean",
    "created_at": "string",
    "owner": {
      "id": "number",
      "nickname": "string"
    }
  }
  ```

#### 프로젝트 상세 조회
```
GET /api/projects/detail/{project_id}/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Response**:
  ```json
  {
    "id": "number",
    "title": "string",
    "description": "string",
    "start_date": "string",
    "end_date": "string",
    "status": "string",
    "is_public": "boolean",
    "created_at": "string",
    "updated_at": "string",
    "owner": {
      "id": "number",
      "nickname": "string",
      "email": "string"
    },
    "members": [
      {
        "id": "number",
        "nickname": "string",
        "role": "string"
      }
    ],
    "files": [
      {
        "id": "number",
        "filename": "string",
        "file_url": "string",
        "uploaded_at": "string"
      }
    ]
  }
  ```

#### 프로젝트 수정
```
PUT /api/projects/detail/{project_id}/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Request Body**: (모든 필드 선택적)
  ```json
  {
    "title": "string",
    "description": "string",
    "start_date": "string",
    "end_date": "string",
    "status": "string"
  }
  ```
- **Response**: 업데이트된 프로젝트 상세 정보

#### 프로젝트 삭제
```
DELETE /api/projects/detail/{project_id}/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Response**: 
  ```json
  {
    "message": "프로젝트가 성공적으로 삭제되었습니다."
  }
  ```

#### 프로젝트 멤버 초대
```
POST /api/projects/{project_id}/invitations/
```
- **Headers**: `Authorization: Bearer {access_token}`
- **Request Body**:
  ```json
  {
    "email": "string",
    "role": "string (member | admin)"
  }
  ```
- **Response**:
  ```json
  {
    "id": "number",
    "project_id": "number",
    "invited_email": "string",
    "role": "string",
    "token": "string",
    "status": "pending",
    "created_at": "string"
  }
  ```

## Request/Response 인터페이스

### TypeScript 인터페이스 정의

```typescript
// Base Types
interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: APIError;
}

interface APIError {
  message: string;
  code?: string;
  field?: string;
  details?: Record<string, any>;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Auth Types
interface User {
  id: number;
  email: string;
  nickname: string;
  profile_image?: string | null;
  company?: string | null;
  phone?: string | null;
  created_at: string;
  email_verified: boolean;
}

interface AuthTokens {
  access: string;
  refresh: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

interface SignupRequest {
  email: string;
  password: string;
  nickname: string;
  phone?: string;
  company?: string;
}

interface SignupResponse {
  user: User;
  tokens: AuthTokens;
}

// Project Types
interface Project {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  status: 'active' | 'completed' | 'archived';
  is_public: boolean;
  created_at: string;
  updated_at: string;
  owner: {
    id: number;
    nickname: string;
    email?: string;
  };
  members_count?: number;
  thumbnail?: string | null;
}

interface ProjectDetail extends Project {
  members: ProjectMember[];
  files: ProjectFile[];
}

interface ProjectMember {
  id: number;
  nickname: string;
  role: 'owner' | 'admin' | 'member';
}

interface ProjectFile {
  id: number;
  filename: string;
  file_url: string;
  uploaded_at: string;
}

interface CreateProjectRequest {
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  status?: string;
  is_public?: boolean;
}
```

## API 클라이언트 구조

### 베이스 클라이언트 클래스

```typescript
// lib/api/base.ts
export class APIClient {
  private baseURL: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;

  constructor(config?: APIClientConfig) {
    this.baseURL = config?.baseURL || process.env.NEXT_PUBLIC_API_URL || 'https://videoplanet.up.railway.app';
    this.timeout = config?.timeout || 30000;
    this.retryAttempts = config?.retryAttempts || 3;
    this.retryDelay = config?.retryDelay || 1000;
  }

  private async request<T>(
    method: string,
    endpoint: string,
    options?: RequestOptions
  ): Promise<APIResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getAccessToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    if (token && !options?.skipAuth) {
      headers['Authorization'] = `Bearer ${token}`;
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
        return this.handleErrorResponse(response);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return this.handleNetworkError(error);
    }
  }

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

    // Handle token expiration
    if (response.status === 401) {
      await this.handleUnauthorized();
    }

    return { success: false, error };
  }

  private handleNetworkError(error: any): APIResponse {
    return {
      success: false,
      error: {
        message: error.message || 'Network error occurred',
        code: 'NETWORK_ERROR',
      },
    };
  }

  private async handleUnauthorized(): Promise<void> {
    // Try to refresh token
    const refreshToken = this.getRefreshToken();
    
    if (refreshToken) {
      const result = await this.refreshAccessToken(refreshToken);
      
      if (!result.success) {
        // Refresh failed, redirect to login
        this.clearTokens();
        window.location.href = '/login';
      }
    } else {
      // No refresh token, redirect to login
      window.location.href = '/login';
    }
  }

  private async refreshAccessToken(refreshToken: string): Promise<APIResponse<AuthTokens>> {
    try {
      const response = await fetch(`${this.baseURL}/api/auth/refresh/`, {
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

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Token management methods
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

  // Public methods
  public setTokens(tokens: AuthTokens): void {
    this.setAccessToken(tokens.access);
    this.setRefreshToken(tokens.refresh);
  }

  public async get<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('GET', endpoint, options);
  }

  public async post<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('POST', endpoint, { ...options, body });
  }

  public async put<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('PUT', endpoint, { ...options, body });
  }

  public async delete<T>(endpoint: string, options?: RequestOptions): Promise<APIResponse<T>> {
    return this.request<T>('DELETE', endpoint, options);
  }
}

// Types
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
```

### 특화된 API 서비스 클래스

```typescript
// lib/api/auth.service.ts
import { APIClient } from './base';

export class AuthService extends APIClient {
  async login(credentials: LoginRequest): Promise<APIResponse<LoginResponse>> {
    const response = await this.post<LoginResponse>('/api/auth/login/', credentials, {
      skipAuth: true,
    });

    if (response.success && response.data) {
      this.setTokens(response.data.tokens);
    }

    return response;
  }

  async signup(data: SignupRequest): Promise<APIResponse<SignupResponse>> {
    const response = await this.post<SignupResponse>('/api/auth/signup/', data, {
      skipAuth: true,
    });

    if (response.success && response.data) {
      this.setTokens(response.data.tokens);
    }

    return response;
  }

  async logout(): Promise<void> {
    this.clearTokens();
    window.location.href = '/login';
  }

  async getCurrentUser(): Promise<APIResponse<User>> {
    return this.get<User>('/api/auth/me/');
  }

  async checkEmailAvailability(email: string): Promise<APIResponse<{ available: boolean }>> {
    return this.post('/api/auth/check-email/', { email }, { skipAuth: true });
  }

  async checkNicknameAvailability(nickname: string): Promise<APIResponse<{ available: boolean }>> {
    return this.post('/api/auth/check-nickname/', { nickname }, { skipAuth: true });
  }
}

// lib/api/project.service.ts
export class ProjectService extends APIClient {
  async getProjects(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
  }): Promise<APIResponse<PaginatedResponse<Project>>> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }

    const endpoint = `/api/projects/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.get<PaginatedResponse<Project>>(endpoint);
  }

  async getProjectDetail(projectId: number): Promise<APIResponse<ProjectDetail>> {
    return this.get<ProjectDetail>(`/api/projects/detail/${projectId}/`);
  }

  async createProject(data: CreateProjectRequest): Promise<APIResponse<Project>> {
    return this.post<Project>('/api/projects/create/', data);
  }

  async updateProject(projectId: number, data: Partial<CreateProjectRequest>): Promise<APIResponse<Project>> {
    return this.put<Project>(`/api/projects/detail/${projectId}/`, data);
  }

  async deleteProject(projectId: number): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/projects/detail/${projectId}/`);
  }

  async inviteMember(projectId: number, data: {
    email: string;
    role: string;
  }): Promise<APIResponse<any>> {
    return this.post(`/api/projects/${projectId}/invitations/`, data);
  }
}
```

## 인증 토큰 관리 전략

### 토큰 저장 및 관리

```typescript
// lib/auth/token-manager.ts
export class TokenManager {
  private static instance: TokenManager;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiryTime: number | null = null;

  private constructor() {
    this.loadTokens();
  }

  static getInstance(): TokenManager {
    if (!TokenManager.instance) {
      TokenManager.instance = new TokenManager();
    }
    return TokenManager.instance;
  }

  private loadTokens(): void {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
      
      const expiryTime = localStorage.getItem('token_expiry');
      this.tokenExpiryTime = expiryTime ? parseInt(expiryTime) : null;
    }
  }

  public setTokens(tokens: AuthTokens): void {
    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;
    
    // JWT는 일반적으로 5분(300초) 유효
    this.tokenExpiryTime = Date.now() + 300000;

    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('token_expiry', this.tokenExpiryTime.toString());
    }

    // 자동 토큰 갱신 설정
    this.setupTokenRefresh();
  }

  public getAccessToken(): string | null {
    // 토큰 만료 확인
    if (this.tokenExpiryTime && Date.now() > this.tokenExpiryTime) {
      this.refreshAccessToken();
    }
    return this.accessToken;
  }

  public getRefreshToken(): string | null {
    return this.refreshToken;
  }

  public clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiryTime = null;

    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token_expiry');
    }
  }

  private setupTokenRefresh(): void {
    if (!this.tokenExpiryTime) return;

    // 만료 1분 전에 갱신
    const refreshTime = this.tokenExpiryTime - Date.now() - 60000;
    
    if (refreshTime > 0) {
      setTimeout(() => {
        this.refreshAccessToken();
      }, refreshTime);
    }
  }

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
        this.setTokens({
          access: data.access,
          refresh: this.refreshToken,
        });
      } else {
        this.handleAuthFailure();
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.handleAuthFailure();
    }
  }

  private handleAuthFailure(): void {
    this.clearTokens();
    // 로그인 페이지로 리다이렉트
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  public isAuthenticated(): boolean {
    return !!this.accessToken && (!this.tokenExpiryTime || Date.now() < this.tokenExpiryTime);
  }
}
```

### Auth Context Provider

```typescript
// contexts/auth.context.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthService } from '@/lib/api/auth.service';
import { TokenManager } from '@/lib/auth/token-manager';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const authService = new AuthService();
  const tokenManager = TokenManager.getInstance();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    setIsLoading(true);
    
    if (tokenManager.isAuthenticated()) {
      try {
        const response = await authService.getCurrentUser();
        if (response.success && response.data) {
          setUser(response.data);
        } else {
          tokenManager.clearTokens();
        }
      } catch (error) {
        console.error('Failed to fetch user:', error);
        tokenManager.clearTokens();
      }
    }
    
    setIsLoading(false);
  };

  const login = async (credentials: LoginRequest) => {
    const response = await authService.login(credentials);
    
    if (response.success && response.data) {
      setUser(response.data.user);
    } else {
      throw new Error(response.error?.message || 'Login failed');
    }
  };

  const signup = async (data: SignupRequest) => {
    const response = await authService.signup(data);
    
    if (response.success && response.data) {
      setUser(response.data.user);
    } else {
      throw new Error(response.error?.message || 'Signup failed');
    }
  };

  const logout = () => {
    setUser(null);
    authService.logout();
  };

  const refreshUser = async () => {
    const response = await authService.getCurrentUser();
    if (response.success && response.data) {
      setUser(response.data);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

## 에러 처리 패턴

### 중앙화된 에러 처리

```typescript
// lib/errors/api-error.ts
export class APIError extends Error {
  public code: string;
  public statusCode: number;
  public details?: any;

  constructor(message: string, code: string, statusCode: number, details?: any) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
  }

  static fromResponse(response: Response, data?: any): APIError {
    const message = data?.message || data?.detail || `HTTP ${response.status}`;
    const code = data?.code || response.status.toString();
    
    return new APIError(message, code, response.status, data);
  }

  isNetworkError(): boolean {
    return this.code === 'NETWORK_ERROR';
  }

  isAuthError(): boolean {
    return this.statusCode === 401 || this.statusCode === 403;
  }

  isValidationError(): boolean {
    return this.statusCode === 400;
  }

  isServerError(): boolean {
    return this.statusCode >= 500;
  }
}

// lib/errors/error-handler.ts
export class ErrorHandler {
  static handle(error: any): { message: string; action?: string } {
    console.error('Error occurred:', error);

    if (error instanceof APIError) {
      return this.handleAPIError(error);
    }

    if (error.name === 'AbortError') {
      return {
        message: '요청 시간이 초과되었습니다. 다시 시도해주세요.',
        action: 'retry',
      };
    }

    if (error.message.includes('fetch')) {
      return {
        message: '네트워크 연결을 확인해주세요.',
        action: 'check_network',
      };
    }

    return {
      message: '알 수 없는 오류가 발생했습니다.',
      action: 'contact_support',
    };
  }

  private static handleAPIError(error: APIError): { message: string; action?: string } {
    if (error.isAuthError()) {
      return {
        message: '인증이 필요합니다. 다시 로그인해주세요.',
        action: 'login',
      };
    }

    if (error.isValidationError()) {
      return {
        message: this.getValidationMessage(error),
        action: 'fix_input',
      };
    }

    if (error.isServerError()) {
      return {
        message: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
        action: 'retry_later',
      };
    }

    return {
      message: error.message || '요청을 처리할 수 없습니다.',
    };
  }

  private static getValidationMessage(error: APIError): string {
    if (error.details?.errors) {
      const errors = error.details.errors;
      const messages = Object.entries(errors)
        .map(([field, msg]) => `${field}: ${msg}`)
        .join(', ');
      return `입력값을 확인해주세요: ${messages}`;
    }
    
    return error.message || '입력값을 확인해주세요.';
  }
}
```

### React Hook for Error Handling

```typescript
// hooks/use-api-error.ts
import { useState, useCallback } from 'react';
import { ErrorHandler } from '@/lib/errors/error-handler';
import { toast } from 'sonner';

export function useAPIError() {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleError = useCallback((error: any) => {
    const { message, action } = ErrorHandler.handle(error);
    
    setError(message);
    toast.error(message);

    if (action === 'login') {
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    }

    return { message, action };
  }, []);

  const execute = useCallback(async <T,>(
    apiCall: () => Promise<T>
  ): Promise<T | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      setIsLoading(false);
      return result;
    } catch (error) {
      handleError(error);
      setIsLoading(false);
      return null;
    }
  }, [handleError]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    isLoading,
    handleError,
    execute,
    clearError,
  };
}
```

## Mock 데이터 및 테스트 전략

### Mock Server Setup (MSW)

```typescript
// mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  // Auth endpoints
  rest.post('/api/auth/login/', (req, res, ctx) => {
    const { email, password } = req.body as LoginRequest;
    
    if (email === 'test@example.com' && password === 'Test1234!') {
      return res(
        ctx.status(200),
        ctx.json<LoginResponse>({
          user: {
            id: 1,
            email: 'test@example.com',
            nickname: 'TestUser',
            profile_image: null,
            company: 'TestCorp',
            phone: '010-1234-5678',
            created_at: '2024-01-01T00:00:00Z',
            email_verified: true,
          },
          tokens: {
            access: 'mock-access-token',
            refresh: 'mock-refresh-token',
          },
        })
      );
    }
    
    return res(
      ctx.status(401),
      ctx.json({
        message: '이메일 또는 비밀번호가 올바르지 않습니다.',
      })
    );
  }),

  rest.post('/api/auth/signup/', (req, res, ctx) => {
    const { email, nickname } = req.body as SignupRequest;
    
    return res(
      ctx.status(201),
      ctx.json<SignupResponse>({
        user: {
          id: 2,
          email,
          nickname,
          profile_image: null,
          company: null,
          phone: null,
          created_at: new Date().toISOString(),
          email_verified: false,
        },
        tokens: {
          access: 'mock-access-token-new',
          refresh: 'mock-refresh-token-new',
        },
      })
    );
  }),

  rest.get('/api/auth/me/', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    
    if (authHeader?.includes('mock-access-token')) {
      return res(
        ctx.status(200),
        ctx.json<User>({
          id: 1,
          email: 'test@example.com',
          nickname: 'TestUser',
          profile_image: null,
          company: 'TestCorp',
          phone: '010-1234-5678',
          created_at: '2024-01-01T00:00:00Z',
          email_verified: true,
        })
      );
    }
    
    return res(
      ctx.status(401),
      ctx.json({ message: 'NEED_ACCESS_TOKEN' })
    );
  }),

  // Project endpoints
  rest.get('/api/projects/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json<PaginatedResponse<Project>>({
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            title: 'Test Project 1',
            description: 'Description for test project 1',
            start_date: '2024-01-01',
            end_date: '2024-12-31',
            status: 'active',
            is_public: false,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            owner: {
              id: 1,
              nickname: 'TestUser',
            },
            members_count: 3,
            thumbnail: null,
          },
          {
            id: 2,
            title: 'Test Project 2',
            description: 'Description for test project 2',
            start_date: '2024-02-01',
            end_date: '2024-11-30',
            status: 'active',
            is_public: true,
            created_at: '2024-02-01T00:00:00Z',
            updated_at: '2024-02-01T00:00:00Z',
            owner: {
              id: 1,
              nickname: 'TestUser',
            },
            members_count: 5,
            thumbnail: null,
          },
        ],
      })
    );
  }),

  rest.post('/api/projects/create/', (req, res, ctx) => {
    const data = req.body as CreateProjectRequest;
    
    return res(
      ctx.status(201),
      ctx.json<Project>({
        id: 3,
        ...data,
        status: data.status || 'active',
        is_public: data.is_public || false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        owner: {
          id: 1,
          nickname: 'TestUser',
        },
      })
    );
  }),
];

// mocks/browser.ts
import { setupWorker } from 'msw';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);

// mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

### 테스트 유틸리티

```typescript
// test-utils/api-mock.ts
export class APIMockBuilder {
  private handlers: any[] = [];

  mockLogin(response?: Partial<LoginResponse>): this {
    this.handlers.push(
      rest.post('/api/auth/login/', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json<LoginResponse>({
            user: {
              id: 1,
              email: 'test@example.com',
              nickname: 'TestUser',
              profile_image: null,
              company: 'TestCorp',
              phone: '010-1234-5678',
              created_at: '2024-01-01T00:00:00Z',
              email_verified: true,
            },
            tokens: {
              access: 'test-access-token',
              refresh: 'test-refresh-token',
            },
            ...response,
          })
        );
      })
    );
    return this;
  }

  mockLoginError(message = '로그인 실패'): this {
    this.handlers.push(
      rest.post('/api/auth/login/', (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json({ message })
        );
      })
    );
    return this;
  }

  mockProjects(projects: Project[]): this {
    this.handlers.push(
      rest.get('/api/projects/', (req, res, ctx) => {
        return res(
          ctx.status(200),
          ctx.json<PaginatedResponse<Project>>({
            count: projects.length,
            next: null,
            previous: null,
            results: projects,
          })
        );
      })
    );
    return this;
  }

  build() {
    return this.handlers;
  }
}

// Usage in tests
import { server } from '@/mocks/server';
import { APIMockBuilder } from '@/test-utils/api-mock';

describe('AuthService', () => {
  beforeEach(() => {
    const mockBuilder = new APIMockBuilder();
    const handlers = mockBuilder
      .mockLogin()
      .mockProjects([])
      .build();
    
    server.use(...handlers);
  });

  it('should login successfully', async () => {
    const authService = new AuthService();
    const result = await authService.login({
      email: 'test@example.com',
      password: 'Test1234!',
    });

    expect(result.success).toBe(true);
    expect(result.data?.user.email).toBe('test@example.com');
  });
});
```

## 타입 안정성 보장 방안

### OpenAPI Schema Generation

```typescript
// scripts/generate-api-types.ts
import { generateApi } from 'swagger-typescript-api';
import path from 'path';

async function generateTypes() {
  try {
    await generateApi({
      name: 'api-types.ts',
      output: path.resolve(process.cwd(), './src/types'),
      url: 'https://videoplanet.up.railway.app/api/schema/',
      httpClientType: 'fetch',
      generateClient: false,
      generateRouteTypes: true,
      generateResponses: true,
      extractRequestParams: true,
      extractRequestBody: true,
    });
    
    console.log('✅ API types generated successfully');
  } catch (error) {
    console.error('❌ Failed to generate API types:', error);
    process.exit(1);
  }
}

generateTypes();
```

### Zod Schema Validation

```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

// Auth Schemas
export const LoginRequestSchema = z.object({
  email: z.string().email('올바른 이메일 형식이 아닙니다'),
  password: z.string().min(8, '비밀번호는 최소 8자 이상이어야 합니다'),
});

export const SignupRequestSchema = z.object({
  email: z.string().email('올바른 이메일 형식이 아닙니다'),
  password: z.string()
    .min(8, '비밀번호는 최소 8자 이상이어야 합니다')
    .regex(/[A-Z]/, '대문자를 포함해야 합니다')
    .regex(/[a-z]/, '소문자를 포함해야 합니다')
    .regex(/[0-9]/, '숫자를 포함해야 합니다')
    .regex(/[!@#$%^&*]/, '특수문자를 포함해야 합니다'),
  nickname: z.string()
    .min(2, '닉네임은 최소 2자 이상이어야 합니다')
    .max(20, '닉네임은 최대 20자까지 가능합니다'),
  phone: z.string().regex(/^010-\d{4}-\d{4}$/, '올바른 전화번호 형식이 아닙니다').optional(),
  company: z.string().max(100, '회사명은 최대 100자까지 가능합니다').optional(),
});

// Project Schemas
export const CreateProjectRequestSchema = z.object({
  title: z.string()
    .min(1, '프로젝트 제목을 입력해주세요')
    .max(200, '제목은 최대 200자까지 가능합니다'),
  description: z.string()
    .min(1, '프로젝트 설명을 입력해주세요')
    .max(1000, '설명은 최대 1000자까지 가능합니다'),
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다'),
  end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다'),
  status: z.enum(['active', 'completed', 'archived']).optional(),
  is_public: z.boolean().optional(),
});

// Type inference
export type LoginRequest = z.infer<typeof LoginRequestSchema>;
export type SignupRequest = z.infer<typeof SignupRequestSchema>;
export type CreateProjectRequest = z.infer<typeof CreateProjectRequestSchema>;
```

### Type Guards

```typescript
// lib/types/guards.ts
export function isAPIError(error: unknown): error is APIError {
  return (
    error instanceof Error &&
    'code' in error &&
    'statusCode' in error
  );
}

export function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'email' in obj &&
    'nickname' in obj
  );
}

export function isProject(obj: unknown): obj is Project {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj &&
    'description' in obj &&
    'owner' in obj
  );
}

export function isPaginatedResponse<T>(
  obj: unknown,
  itemGuard: (item: unknown) => item is T
): obj is PaginatedResponse<T> {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'count' in obj &&
    'results' in obj &&
    Array.isArray((obj as any).results) &&
    (obj as any).results.every(itemGuard)
  );
}
```

### API Response Validator

```typescript
// lib/api/response-validator.ts
import { z } from 'zod';

export class ResponseValidator {
  static validate<T>(
    data: unknown,
    schema: z.ZodSchema<T>
  ): { success: true; data: T } | { success: false; errors: z.ZodError } {
    try {
      const validated = schema.parse(data);
      return { success: true, data: validated };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return { success: false, errors: error };
      }
      throw error;
    }
  }

  static async validateAsync<T>(
    data: unknown,
    schema: z.ZodSchema<T>
  ): Promise<T> {
    return schema.parseAsync(data);
  }
}

// Usage
const loginResponse = await apiClient.post('/api/auth/login/', credentials);
const validated = ResponseValidator.validate(loginResponse, LoginResponseSchema);

if (validated.success) {
  // Type-safe access to validated.data
  console.log(validated.data.user.email);
} else {
  // Handle validation errors
  console.error(validated.errors.format());
}
```

## 사용 예제

### 로그인 플로우

```typescript
// app/login/page.tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/auth.context';
import { LoginRequestSchema } from '@/lib/validation/schemas';
import { useAPIError } from '@/hooks/use-api-error';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const { execute, error, isLoading } = useAPIError();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate input
    const validation = LoginRequestSchema.safeParse(formData);
    if (!validation.success) {
      // Handle validation errors
      return;
    }

    // Execute login
    const result = await execute(() => login(validation.data));
    
    if (result) {
      router.push('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
}
```

### 프로젝트 목록

```typescript
// app/projects/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { ProjectService } from '@/lib/api/project.service';
import { useAPIError } from '@/hooks/use-api-error';
import type { Project, PaginatedResponse } from '@/types/api';

export default function ProjectsPage() {
  const projectService = new ProjectService();
  const { execute, error, isLoading } = useAPIError();
  
  const [projects, setProjects] = useState<Project[]>([]);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0,
  });

  useEffect(() => {
    loadProjects();
  }, [pagination.page]);

  const loadProjects = async () => {
    const result = await execute(async () => {
      const response = await projectService.getProjects({
        page: pagination.page,
        page_size: pagination.pageSize,
      });
      
      if (response.success && response.data) {
        return response.data;
      }
      
      throw new Error(response.error?.message || 'Failed to load projects');
    });

    if (result) {
      setProjects(result.results);
      setPagination(prev => ({ ...prev, total: result.count }));
    }
  };

  return (
    <div>
      {isLoading && <div>Loading...</div>}
      {error && <div className="error">{error}</div>}
      
      {projects.map(project => (
        <div key={project.id}>
          <h3>{project.title}</h3>
          <p>{project.description}</p>
        </div>
      ))}
    </div>
  );
}
```

## 개발 환경 설정

### 환경 변수

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://videoplanet.up.railway.app
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_API_RETRY_ATTEMPTS=3
NEXT_PUBLIC_API_RETRY_DELAY=1000
```

### Package.json Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "generate:api-types": "tsx scripts/generate-api-types.ts",
    "mock:start": "tsx mocks/start.ts"
  }
}
```

### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true,
    "noImplicitAny": true,
    "paths": {
      "@/lib/*": ["./src/lib/*"],
      "@/types/*": ["./src/types/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/contexts/*": ["./src/contexts/*"],
      "@/mocks/*": ["./src/mocks/*"]
    }
  }
}
```

## 마이그레이션 가이드

### 기존 코드에서 마이그레이션

```typescript
// Before (기존 방식)
fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
})
.then(res => res.json())
.then(data => {
  localStorage.setItem('token', data.token);
})
.catch(err => console.error(err));

// After (새로운 방식)
const authService = new AuthService();
const result = await authService.login({ email, password });

if (result.success) {
  // Tokens are automatically stored
  console.log('Login successful:', result.data.user);
} else {
  console.error('Login failed:', result.error.message);
}
```

## 모니터링 및 디버깅

### API 호출 로깅

```typescript
// lib/api/logger.ts
export class APILogger {
  static log(method: string, endpoint: string, data?: any): void {
    if (process.env.NODE_ENV === 'development') {
      console.group(`🚀 API ${method} ${endpoint}`);
      console.log('Request:', data);
      console.groupEnd();
    }
  }

  static logResponse(endpoint: string, response: any): void {
    if (process.env.NODE_ENV === 'development') {
      console.group(`✅ Response ${endpoint}`);
      console.log('Data:', response);
      console.groupEnd();
    }
  }

  static logError(endpoint: string, error: any): void {
    console.group(`❌ Error ${endpoint}`);
    console.error('Error:', error);
    console.groupEnd();
  }
}
```

### Network Inspector

```typescript
// lib/debug/network-inspector.ts
export class NetworkInspector {
  private static requests: Map<string, RequestInfo> = new Map();

  static start(): void {
    if (typeof window === 'undefined') return;

    const originalFetch = window.fetch;
    
    window.fetch = async (...args) => {
      const [url, config] = args;
      const requestId = `${Date.now()}-${Math.random()}`;
      
      this.requests.set(requestId, {
        url: url.toString(),
        method: config?.method || 'GET',
        startTime: Date.now(),
      });

      try {
        const response = await originalFetch(...args);
        
        this.requests.get(requestId)!.endTime = Date.now();
        this.requests.get(requestId)!.status = response.status;
        
        return response;
      } catch (error) {
        this.requests.get(requestId)!.error = error;
        throw error;
      }
    };
  }

  static getRequests(): RequestInfo[] {
    return Array.from(this.requests.values());
  }

  static clear(): void {
    this.requests.clear();
  }
}

interface RequestInfo {
  url: string;
  method: string;
  startTime: number;
  endTime?: number;
  status?: number;
  error?: any;
}
```

## 성능 최적화

### Request Deduplication

```typescript
// lib/api/request-deduplicator.ts
export class RequestDeduplicator {
  private static cache = new Map<string, Promise<any>>();
  private static ttl = 5000; // 5 seconds

  static async dedupe<T>(
    key: string,
    fetcher: () => Promise<T>
  ): Promise<T> {
    if (this.cache.has(key)) {
      return this.cache.get(key)!;
    }

    const promise = fetcher();
    this.cache.set(key, promise);

    // Clean up after TTL
    setTimeout(() => {
      this.cache.delete(key);
    }, this.ttl);

    return promise;
  }
}

// Usage
const projects = await RequestDeduplicator.dedupe(
  'projects-list',
  () => projectService.getProjects()
);
```

### Response Caching

```typescript
// lib/api/response-cache.ts
export class ResponseCache {
  private static cache = new Map<string, CachedResponse>();

  static set(key: string, data: any, ttl = 60000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  static get(key: string): any | null {
    const cached = this.cache.get(key);
    
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }

  static clear(): void {
    this.cache.clear();
  }
}

interface CachedResponse {
  data: any;
  timestamp: number;
  ttl: number;
}
```

## 보안 고려사항

### XSS Prevention

```typescript
// lib/security/sanitizer.ts
import DOMPurify from 'isomorphic-dompurify';

export class Sanitizer {
  static sanitizeHTML(html: string): string {
    return DOMPurify.sanitize(html);
  }

  static sanitizeInput(input: string): string {
    return input
      .replace(/[<>]/g, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+=/gi, '');
  }

  static sanitizeURL(url: string): string {
    try {
      const parsed = new URL(url);
      
      // Only allow http(s) protocols
      if (!['http:', 'https:'].includes(parsed.protocol)) {
        throw new Error('Invalid protocol');
      }
      
      return parsed.toString();
    } catch {
      return '';
    }
  }
}
```

### CSRF Protection

```typescript
// lib/security/csrf.ts
export class CSRFProtection {
  private static tokenKey = 'csrf_token';

  static async getToken(): Promise<string> {
    let token = sessionStorage.getItem(this.tokenKey);
    
    if (!token) {
      token = await this.fetchToken();
      sessionStorage.setItem(this.tokenKey, token);
    }
    
    return token;
  }

  private static async fetchToken(): Promise<string> {
    const response = await fetch('/api/csrf-token/');
    const data = await response.json();
    return data.token;
  }

  static addToHeaders(headers: HeadersInit): HeadersInit {
    const token = sessionStorage.getItem(this.tokenKey);
    
    if (token) {
      return {
        ...headers,
        'X-CSRF-Token': token,
      };
    }
    
    return headers;
  }
}
```

## 결론

이 가이드는 VideoPlanet 프로젝트의 백엔드 API 통합을 위한 포괄적인 전략을 제공합니다. 
주요 특징:

1. **타입 안정성**: TypeScript와 Zod를 활용한 런타임 및 컴파일 타임 타입 검증
2. **에러 처리**: 중앙화된 에러 처리 및 사용자 친화적 메시지
3. **인증 관리**: JWT 토큰 자동 갱신 및 보안 저장
4. **테스트 지원**: MSW를 활용한 모킹 및 테스트 유틸리티
5. **성능 최적화**: 요청 중복 제거, 응답 캐싱
6. **보안**: XSS, CSRF 방어 메커니즘

이 구조를 기반으로 안정적이고 확장 가능한 API 통합을 구현할 수 있습니다.