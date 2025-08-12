'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { useAuth } from '@/contexts/auth.context';
import { toast } from 'sonner';
import styles from './login.module.scss';

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isLoading, isAuthenticated } = useAuth();
  
  const [inputs, setInputs] = useState({
    email: '',
    password: '',
  });
  const [loginMessage, setLoginMessage] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  //   
  const uid = searchParams.get('uid');
  const token = searchParams.get('token');
  const returnUrl = searchParams.get('returnUrl');
  const fromPage = searchParams.get('from');
  const message = searchParams.get('message');

  //    
  useEffect(() => {
    if (isAuthenticated) {
      if (uid && token) {
        router.push(`/EmailCheck?uid=${uid}&token=${token}`);
      } else if (returnUrl) {
        router.push(returnUrl);
      } else if (fromPage) {
        router.push(fromPage);
      } else {
        router.push('/cmshome');
      }
    }
  }, [isAuthenticated, uid, token, returnUrl, fromPage, router]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setInputs(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleLogin = async () => {
    console.log('[LoginPage] 로그인 시도');
    console.log('[LoginPage] 입력값:', inputs);
    
    if (!inputs.email || !inputs.password) {
      if (!inputs.email) {
        setLoginMessage('이메일을 입력해주세요.');
      } else {
        setLoginMessage('비밀번호를 입력해주세요.');
      }
      return;
    }

    if (isLoggingIn) {
      console.log('[LoginPage] 이미 로그인 처리 중...');
      return;
    }

    setIsLoggingIn(true);
    setLoginMessage('');
    console.log('[LoginPage] 로그인 API 호출 시작');
    console.log('[LoginPage] API URL:', process.env.NEXT_PUBLIC_API_URL);

    try {
      const success = await login({ email: inputs.email, password: inputs.password });
      console.log('[LoginPage] 로그인 결과:', success);
      
      if (success) {
        toast.success('로그인되었습니다!');
        
        //  
        const redirectUrl = uid && token 
          ? `/EmailCheck?uid=${uid}&token=${token}`
          : returnUrl || fromPage || '/cmshome';
        
        console.log('[LoginPage] 리다이렉트:', redirectUrl);
        router.push(redirectUrl);
      } else {
        setLoginMessage('이메일 또는 비밀번호가 올바르지 않습니다.');
      }
    } catch (error: any) {
      console.error('[LoginPage] 로그인 오류:', error);
      
      if (error.response?.status === 401) {
        setLoginMessage('이메일 또는 비밀번호가 올바르지 않습니다.');
      } else if (error.response?.status === 403 && error.response?.data?.error_code === 'EMAIL_NOT_VERIFIED') {
        setLoginMessage(error.response.data.message || '이메일 인증이 필요합니다.');
      } else if (error.response?.data?.message) {
        setLoginMessage(error.response.data.message);
      } else {
        setLoginMessage('로그인 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      console.log('[LoginPage] Enter 키 눌림');
      e.preventDefault();
      handleLogin();
    }
  };

  const handleSocialLogin = (provider: string) => {
    toast.info(`${provider} 로그인 준비 중입니다.`);
  };

  return (
    <div className={styles.user}>
      {/*    */}
      <div className={styles.intro}>
        <div className={styles.intro_wrap}>
          <h1 className={styles.logo}>
            <Link href="/">
              <Image 
                src="/images/logo/vlanet-logo.svg" 
                alt="Vlanet" 
                width={120} 
                height={40}
                priority
                unoptimized
              />
            </Link>
          </h1>
          <div className={styles.slogun}>
            영상 피드백의 새로운 기준
            <br />
            빠르고 정확한 협업을 경험하세요<br />
            <span>브이라넷과 함께</span>
          </div>
          <div className={styles.etc}>
            <ul>
              <li>
                Connect
                <br /> with each other
              </li>
              <li>
                Easy
                <br /> Feedback
              </li>
              <li>
                Study
                <br /> Together
              </li>
            </ul>
            <div>
              vlanet to
              <br /> connection
            </div>
          </div>
        </div>
      </div>

      {/*    */}
      <div className={styles.form}>
        <div className={styles.form_wrap}>
          <div className={styles.title}>로그인</div>
          
          {/*    */}
          {message && (
            <div style={{
              background: 'linear-gradient(135deg, #E8EBFF 0%, #D1D8FF 100%)',
              border: '1px solid #1631F8',
              borderRadius: '8px',
              padding: '16px',
              marginTop: '24px',
              marginBottom: '-20px',
              textAlign: 'center'
            }}>
              <p style={{
                margin: 0,
                color: '#1631F8',
                fontWeight: '600',
                fontSize: '15px'
              }}>
                 {message}
              </p>
            </div>
          )}
          
          <input
            type="email"
            name="email"
            placeholder="이메일을 입력하세요"
            className={`${styles.ty01} ${styles.mt50}`}
            value={inputs.email}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            autoComplete="email"
          />

          <input
            type="password"
            name="password"
            placeholder="비밀번호를 입력하세요"
            className={`${styles.ty01} ${styles.mt10}`}
            value={inputs.password}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            autoComplete="current-password"
          />
          
          {loginMessage && (
            <div className={styles.error}>{loginMessage}</div>
          )}
          
          <div 
            className={styles.find_link}
            onClick={() => router.push('/resetpw')}
          >
            비밀번호를 잊으셨나요?
          </div>
          
          <button 
            type="button"
            className={`${styles.submit} ${styles.mt20}`}
            onClick={(e) => {
              e.preventDefault();
              console.log('[LoginPage] 로그인 버튼 클릭');
              handleLogin();
            }}
            disabled={isLoggingIn || !inputs.email || !inputs.password}
          >
            {isLoggingIn ? '로그인 중...' : '로그인'}
          </button>
          
          <div className={styles.signup_link}>
            계정이 없으신가요?
            <span onClick={() => router.push('/signup')}>회원가입</span>
          </div>

          <div className={styles.line}></div>
          
          <div className={styles.sns_login}>
            <ul>
              <li 
                className={styles.google}
                onClick={() => handleSocialLogin('Google')}
              >
                Google
              </li>
              <li 
                className={styles.kakao}
                onClick={() => handleSocialLogin('Kakao')}
              >
                Kakao
              </li>
              <li 
                className={styles.naver}
                onClick={() => handleSocialLogin('Naver')}
              >
                Naver
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className={styles.user}>
        <div className={styles.intro}></div>
        <div className={styles.form}>
          <div className={styles.form_wrap}>
            <div className={styles.title}></div>
            <div style={{ textAlign: 'center', marginTop: '50px', color: '#999' }}>
              로딩 중...
            </div>
          </div>
        </div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}