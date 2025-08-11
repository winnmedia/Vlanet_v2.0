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
    console.log('[LoginPage]   ');
    console.log('[LoginPage] :', inputs);
    
    if (!inputs.email || !inputs.password) {
      if (!inputs.email) {
        setLoginMessage(' .');
      } else {
        setLoginMessage(' .');
      }
      return;
    }

    if (isLoggingIn) {
      console.log('[LoginPage]   ...');
      return;
    }

    setIsLoggingIn(true);
    setLoginMessage('');
    console.log('[LoginPage]  API  ');
    console.log('[LoginPage] API URL:', process.env.NEXT_PUBLIC_API_URL);

    try {
      const success = await login({ email: inputs.email, password: inputs.password });
      console.log('[LoginPage]  :', success);
      
      if (success) {
        toast.success(' !');
        
        //  
        const redirectUrl = uid && token 
          ? `/EmailCheck?uid=${uid}&token=${token}`
          : returnUrl || fromPage || '/cmshome';
        
        console.log('[LoginPage] :', redirectUrl);
        router.push(redirectUrl);
      } else {
        setLoginMessage('    .');
      }
    } catch (error: any) {
      console.error('[LoginPage]  :', error);
      
      if (error.response?.status === 401) {
        setLoginMessage('    .');
      } else if (error.response?.status === 403 && error.response?.data?.error_code === 'EMAIL_NOT_VERIFIED') {
        setLoginMessage(error.response.data.message || '  .');
      } else if (error.response?.data?.message) {
        setLoginMessage(error.response.data.message);
      } else {
        setLoginMessage('  .    .');
      }
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      console.log('[LoginPage] Enter  ');
      e.preventDefault();
      handleLogin();
    }
  };

  const handleSocialLogin = (provider: string) => {
    toast.info(`${provider}  .`);
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
             
            <br />
              <br />
            <span>  </span>
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
          <div className={styles.title}></div>
          
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
            placeholder=""
            className={`${styles.ty01} ${styles.mt50}`}
            value={inputs.email}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            autoComplete="email"
          />

          <input
            type="password"
            name="password"
            placeholder=""
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
             
          </div>
          
          <button 
            type="button"
            className={`${styles.submit} ${styles.mt20}`}
            onClick={(e) => {
              e.preventDefault();
              console.log('[LoginPage]    ');
              handleLogin();
            }}
            disabled={isLoggingIn || !inputs.email || !inputs.password}
          >
            {isLoggingIn ? ' ...' : ''}
          </button>
          
          <div className={styles.signup_link}>
             ?
            <span onClick={() => router.push('/signup')}> </span>
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
               ...
            </div>
          </div>
        </div>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}