import { NextRequest, NextResponse } from 'next/server';

/**
 * 로그인 API 엔드포인트
 * POST /api/auth/login
 */
export async function POST(request: NextRequest) {
  try {
    // 요청 바디 파싱
    const body = await request.json();
    const { email, password } = body;

    // 입력 검증
    if (!email || !password) {
      return NextResponse.json(
        {
          success: false,
          error: {
            message: '이메일과 비밀번호를 입력해주세요.',
            code: 'MISSING_CREDENTIALS'
          }
        },
        { status: 400 }
      );
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        {
          success: false,
          error: {
            message: '올바른 이메일 형식을 입력해주세요.',
            code: 'INVALID_EMAIL_FORMAT'
          }
        },
        { status: 400 }
      );
    }

    // 백엔드 API 호출
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://videoplanet.up.railway.app';
    console.log('[API Route] 백엔드 로그인 요청:', { email, backendUrl });

    const backendResponse = await fetch(`${backendUrl}/api/users/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const responseData = await backendResponse.json();
    console.log('[API Route] 백엔드 응답:', { 
      status: backendResponse.status, 
      ok: backendResponse.ok,
      data: responseData 
    });

    // 백엔드 응답 처리
    if (backendResponse.ok && responseData) {
      return NextResponse.json({
        success: true,
        data: {
          access: responseData.access,
          refresh: responseData.refresh,
          user: responseData.user,
          vridge_session: responseData.vridge_session
        }
      });
    } else {
      // 백엔드 에러 처리
      const errorMessage = responseData?.detail || 
                          responseData?.message || 
                          responseData?.error || 
                          '로그인에 실패했습니다.';
      
      return NextResponse.json(
        {
          success: false,
          error: {
            message: errorMessage,
            code: 'LOGIN_FAILED',
            status: backendResponse.status
          }
        },
        { status: backendResponse.status === 401 ? 401 : 400 }
      );
    }

  } catch (error) {
    console.error('[API Route] 로그인 처리 중 오류:', error);
    
    // 네트워크 오류 처리
    if (error instanceof Error && error.name === 'TypeError') {
      return NextResponse.json(
        {
          success: false,
          error: {
            message: '서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.',
            code: 'NETWORK_ERROR'
          }
        },
        { status: 503 }
      );
    }

    // 일반적인 서버 오류
    return NextResponse.json(
      {
        success: false,
        error: {
          message: '서버 오류가 발생했습니다.',
          code: 'INTERNAL_ERROR'
        }
      },
      { status: 500 }
    );
  }
}

/**
 * 로그인 엔드포인트는 POST 요청만 지원
 */
export async function GET() {
  return NextResponse.json(
    {
      success: false,
      error: {
        message: 'POST 요청만 지원됩니다.',
        code: 'METHOD_NOT_ALLOWED'
      }
    },
    { status: 405 }
  );
}