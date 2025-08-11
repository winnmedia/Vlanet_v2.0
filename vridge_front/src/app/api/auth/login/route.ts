import { NextRequest, NextResponse } from 'next/server';

/**
 *  API 
 * POST /api/auth/login
 */
export async function POST(request: NextRequest) {
  try {
    //   
    const body = await request.json();
    const { email, password } = body;

    //  
    if (!email || !password) {
      return NextResponse.json(
        {
          success: false,
          error: {
            message: '  .',
            code: 'MISSING_CREDENTIALS'
          }
        },
        { status: 400 }
      );
    }

    //   
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        {
          success: false,
          error: {
            message: '   .',
            code: 'INVALID_EMAIL_FORMAT'
          }
        },
        { status: 400 }
      );
    }

    //  API 
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://videoplanet.up.railway.app';
    console.log('[API Route]   :', { email, backendUrl });

    const backendResponse = await fetch(`${backendUrl}/api/users/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const responseData = await backendResponse.json();
    console.log('[API Route]  :', { 
      status: backendResponse.status, 
      ok: backendResponse.ok,
      data: responseData 
    });

    //   
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
      //   
      const errorMessage = responseData?.detail || 
                          responseData?.message || 
                          responseData?.error || 
                          ' .';
      
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
    console.error('[API Route]    :', error);
    
    //   
    if (error instanceof Error && error.name === 'TypeError') {
      return NextResponse.json(
        {
          success: false,
          error: {
            message: '   .    .',
            code: 'NETWORK_ERROR'
          }
        },
        { status: 503 }
      );
    }

    //   
    return NextResponse.json(
      {
        success: false,
        error: {
          message: '  .',
          code: 'INTERNAL_ERROR'
        }
      },
      { status: 500 }
    );
  }
}

/**
 *   POST  
 */
export async function GET() {
  return NextResponse.json(
    {
      success: false,
      error: {
        message: 'POST  .',
        code: 'METHOD_NOT_ALLOWED'
      }
    },
    { status: 405 }
  );
}