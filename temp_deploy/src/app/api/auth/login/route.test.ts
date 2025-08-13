import { describe, it, expect, beforeEach, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { POST, GET } from './route';

// Fetch Mock 설정
global.fetch = vi.fn();

describe('/api/auth/login', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.NEXT_PUBLIC_API_URL = 'https://test-backend.com';
  });

  describe('POST 요청', () => {
    it('유효한 자격증명으로 로그인 성공', async () => {
      const mockBackendResponse = {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: { id: 1, email: 'test@example.com' },
        vridge_session: 'mock-session'
      };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockBackendResponse
      });

      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com', password: 'password123' })
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data.access).toBe('mock-access-token');
      expect(data.data.user.email).toBe('test@example.com');
      expect(fetch).toHaveBeenCalledWith(
        'https://test-backend.com/api/users/login/',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com', password: 'password123' })
        })
      );
    });

    it('잘못된 자격증명으로 로그인 실패', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: '이메일 또는 비밀번호가 올바르지 않습니다.' })
      });

      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com', password: 'wrong-password' })
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(401);
      expect(data.success).toBe(false);
      expect(data.error.message).toBe('이메일 또는 비밀번호가 올바르지 않습니다.');
      expect(data.error.code).toBe('LOGIN_FAILED');
    });

    it('필수 필드 누락 시 400 에러 반환', async () => {
      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com' })
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('MISSING_CREDENTIALS');
    });

    it('잘못된 이메일 형식 시 400 에러 반환', async () => {
      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'invalid-email', password: 'password123' })
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('INVALID_EMAIL_FORMAT');
    });

    it('네트워크 오류 시 503 에러 반환', async () => {
      (fetch as any).mockRejectedValueOnce(new TypeError('Network error'));

      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com', password: 'password123' })
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(503);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('NETWORK_ERROR');
    });

    it('JSON 파싱 오류 시 500 에러 반환', async () => {
      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: 'invalid-json'
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('INTERNAL_ERROR');
    });
  });

  describe('GET 요청', () => {
    it('GET 요청 시 405 에러 반환', async () => {
      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(405);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('METHOD_NOT_ALLOWED');
    });
  });
});