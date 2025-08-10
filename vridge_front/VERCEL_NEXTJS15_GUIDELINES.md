# Next.js 15 + Vercel 배포 가이드라인

## 1. 자주 발생하는 오류와 해결법

### ReferenceError: currentUser is not defined
**원인**: 서버 컴포넌트에서 클라이언트 전용 코드를 사용하거나, 변수가 정의되지 않은 상태로 참조

**해결법**:
```typescript
// ❌ 잘못된 예
export default function ProfilePage() {
  return <div>{currentUser.name}</div>; // currentUser가 정의되지 않음
}

// ✅ 올바른 예 1: 조건부 렌더링
export default function ProfilePage({ user }) {
  return <div>{user?.name || 'Guest'}</div>;
}

// ✅ 올바른 예 2: 클라이언트 컴포넌트 사용
'use client';
import { useUser } from '@/hooks/useUser';

export default function ProfilePage() {
  const { currentUser } = useUser();
  return <div>{currentUser?.name}</div>;
}
```

### Function Runtimes must have a valid version
**원인**: vercel.json에 잘못된 런타임 버전 지정

**해결법**:
```json
// ❌ 잘못된 예
{
  "functions": {
    "runtime": "nodejs16.x" // 지원 종료된 버전
  }
}

// ✅ 올바른 예
{
  "functions": {
    "app/api/**.ts": {
      "runtime": "nodejs20.x" // 또는 nodejs18.x
    }
  }
}
```

### Module not found 오류
**원인**: 의존성 누락 또는 잘못된 import 경로

**해결법**:
```bash
# 의존성 재설치
rm -rf node_modules package-lock.json
npm install

# 캐시 정리
npm cache clean --force
```

## 2. Next.js 15 핵심 변경사항

### App Router 사용
```typescript
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}

// app/page.tsx
export default function HomePage() {
  return <main>홈페이지</main>;
}
```

### 서버 컴포넌트 vs 클라이언트 컴포넌트
```typescript
// 서버 컴포넌트 (기본값)
// app/components/ServerComponent.tsx
async function ServerComponent() {
  const data = await fetch('https://api.example.com/data');
  return <div>{data}</div>;
}

// 클라이언트 컴포넌트
// app/components/ClientComponent.tsx
'use client'; // 필수!

import { useState } from 'react';

export default function ClientComponent() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### 서버 액션
```typescript
// app/actions.ts
'use server';

export async function createUser(formData: FormData) {
  const name = formData.get('name');
  // 데이터베이스 작업
  return { success: true };
}

// app/components/Form.tsx
import { createUser } from '@/app/actions';

export default function Form() {
  return (
    <form action={createUser}>
      <input name="name" />
      <button type="submit">Submit</button>
    </form>
  );
}
```

## 3. 금지된 설정 및 패턴

### ❌ 하지 말아야 할 것들

1. **getServerSideProps/getStaticProps 사용 (App Router에서)**
```typescript
// ❌ Pages Router 방식 (App Router에서 사용 불가)
export async function getServerSideProps() {
  return { props: {} };
}

// ✅ App Router 방식
async function Page() {
  const data = await fetchData();
  return <div>{data}</div>;
}
```

2. **window/document를 서버 컴포넌트에서 직접 사용**
```typescript
// ❌ 서버 컴포넌트에서 직접 사용
export default function Component() {
  const width = window.innerWidth; // 오류!
  return <div>{width}</div>;
}

// ✅ useEffect 내에서 사용
'use client';
import { useEffect, useState } from 'react';

export default function Component() {
  const [width, setWidth] = useState(0);
  
  useEffect(() => {
    setWidth(window.innerWidth);
  }, []);
  
  return <div>{width}</div>;
}
```

3. **환경 변수 클라이언트 노출**
```typescript
// ❌ 서버 전용 환경 변수를 클라이언트에 노출
const apiKey = process.env.SECRET_API_KEY; // 클라이언트에서 undefined

// ✅ 클라이언트용 환경 변수 사용
const publicKey = process.env.NEXT_PUBLIC_API_KEY; // NEXT_PUBLIC_ 접두사 필수
```

## 4. Vercel 최적화 팁

### 이미지 최적화
```typescript
import Image from 'next/image';

// Vercel이 자동으로 최적화
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // LCP 이미지에 사용
  placeholder="blur" // 블러 플레이스홀더
  blurDataURL="..." // base64 블러 이미지
/>
```

### 정적 생성 우선
```typescript
// app/posts/[id]/page.tsx
export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({
    id: post.id.toString(),
  }));
}

export default async function PostPage({ params }) {
  const post = await getPost(params.id);
  return <article>{post.title}</article>;
}
```

### Edge Runtime 활용
```typescript
// app/api/hello/route.ts
export const runtime = 'edge'; // Edge Runtime 사용

export async function GET() {
  return new Response('Hello from Edge!');
}
```

## 5. 디버깅 팁

### Vercel 로그 확인
```bash
# Vercel CLI 설치
npm i -g vercel

# 로그 확인
vercel logs --follow

# 특정 함수 로그
vercel logs [function-name]
```

### 로컬에서 Vercel 환경 시뮬레이션
```bash
# Vercel 환경과 동일하게 빌드
vercel build

# 프로덕션 모드로 실행
vercel dev --prod
```

### 환경 변수 디버깅
```typescript
// app/api/debug/route.ts (개발 환경에서만!)
export async function GET() {
  if (process.env.NODE_ENV !== 'development') {
    return new Response('Not allowed', { status: 403 });
  }
  
  return Response.json({
    env: {
      NODE_ENV: process.env.NODE_ENV,
      VERCEL: process.env.VERCEL,
      VERCEL_ENV: process.env.VERCEL_ENV,
      // 다른 환경 변수들...
    }
  });
}
```

## 6. 성능 최적화

### 번들 크기 분석
```bash
# 번들 분석기 설치
npm install @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // 설정...
});

# 분석 실행
ANALYZE=true npm run build
```

### 동적 임포트 활용
```typescript
import dynamic from 'next/dynamic';

// 무거운 컴포넌트 동적 로딩
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
  ssr: false, // 클라이언트에서만 렌더링
});
```

### 캐싱 전략
```typescript
// app/api/data/route.ts
export async function GET() {
  const data = await fetch('https://api.example.com/data', {
    next: { 
      revalidate: 3600, // 1시간 캐싱
      tags: ['data'] // 캐시 태그
    }
  });
  
  return Response.json(data);
}

// 캐시 무효화
import { revalidateTag } from 'next/cache';
revalidateTag('data');
```

## 7. 체크리스트

배포 전 확인사항:
- [ ] 모든 'use client' 지시어가 올바른 위치에 있는가?
- [ ] 환경 변수가 Vercel에 설정되어 있는가?
- [ ] vercel.json이 유효한가?
- [ ] 빌드 크기가 50MB 이하인가?
- [ ] API 라우트가 10초 이내에 응답하는가?
- [ ] 이미지가 최적화되어 있는가?
- [ ] 에러 페이지(error.tsx, not-found.tsx)가 구현되어 있는가?
- [ ] 메타데이터가 올바르게 설정되어 있는가?