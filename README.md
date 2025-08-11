# VideoPlanet

영상 제작자들을 위한 통합 프로젝트 관리 플랫폼

## 🚀 기술 스택

- **Framework**: Next.js 15.1 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.4
- **State Management**: Zustand 5.x
- **Server State**: TanStack Query 5.x
- **HTTP Client**: Axios 1.7.x
- **Forms**: React Hook Form + Zod
- **Animation**: Framer Motion 11.x
- **Icons**: Lucide React

## 📋 주요 기능

### 1. 인증 시스템
- JWT 기반 토큰 인증
- 소셜 로그인 (Google, Kakao)
- 자동 토큰 갱신
- 보안 강화된 세션 관리

### 2. 프로젝트 관리
- 프로젝트 생성, 수정, 삭제 (CRUD)
- 팀 멤버 관리 및 권한 설정
- 실시간 협업 기능
- 파일 업로드 및 공유

### 3. 영상 기획 시스템
- AI 기반 스토리텔링 도구
- 스토리보드 생성 및 편집
- 콘티 자동 생성
- 전문 기획안 다운로드

### 4. 피드백 시스템
- 타임라인 기반 피드백
- 실시간 댓글 및 리뷰
- 상태 관리 (대기중, 진행중, 완료)
- 우선순위 설정

## 🛠️ 개발 환경 설정

### 필수 조건
- Node.js 18.x 이상
- npm 8.x 이상

### 설치
```bash
# 프로젝트 클론
git clone https://github.com/your-repo/videoplanet-clean.git
cd videoplanet-clean

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env.local
# .env.local 파일을 편집하여 필요한 환경 변수 설정
```

### 개발 서버 실행
```bash
# 개발 서버 시작
npm run dev

# 브라우저에서 http://localhost:3000 접속
```

## 📁 프로젝트 구조

```
src/
├── app/                    # Next.js App Router
│   ├── globals.css        # 전역 스타일
│   ├── layout.tsx         # 루트 레이아웃
│   ├── page.tsx          # 홈페이지
│   └── providers.tsx     # 전역 프로바이더
├── components/            # 재사용 가능한 컴포넌트
│   ├── auth/             # 인증 관련 컴포넌트
│   ├── projects/         # 프로젝트 관련 컴포넌트
│   ├── ui/              # 기본 UI 컴포넌트
│   └── layout/          # 레이아웃 컴포넌트
├── contexts/             # React Context
├── hooks/               # 커스텀 훅
├── lib/                 # 유틸리티 라이브러리
│   ├── api/            # API 클라이언트
│   ├── auth/           # 인증 관련
│   ├── validation/     # 스키마 검증
│   └── errors/         # 에러 처리
├── store/              # Zustand 스토어
├── types/              # TypeScript 타입 정의
└── utils/              # 유틸리티 함수
```

## 🔧 주요 스크립트

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 빌드된 애플리케이션 실행
npm run start

# 코드 검사
npm run lint

# 코드 포맷팅
npm run format

# 타입 체크
npm run type-check

# 테스트 실행
npm run test

# 테스트 커버리지
npm run test:coverage
```

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary**: #1631F8 (브랜드 주요 색상)
- **Primary Dark**: #0F23C9 (호버/액티브 상태)
- **Secondary**: #6C5CE7 (보조 색상)
- **Accent**: #00D4FF (강조 색상)

### 컴포넌트 스타일
- 모든 컴포넌트는 Tailwind CSS 기반으로 구현
- 일관된 디자인 토큰 사용
- 반응형 디자인 지원
- 다크 모드 지원

## 🔒 보안

### 인증 & 권한
- JWT 토큰 기반 인증
- httpOnly 쿠키를 통한 토큰 저장
- 자동 토큰 갱신
- RBAC (Role-Based Access Control)

### 보안 헤더
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin

### 입력 검증
- Zod를 통한 스키마 검증
- XSS 방지
- CSRF 보호

## 📱 반응형 디자인

### 브레이크포인트
- **Mobile**: < 640px
- **Tablet**: 640px ~ 1024px
- **Desktop**: > 1024px

### 모바일 최적화
- 터치 인터랙션 최적화
- 안전 영역 지원
- 모바일 네비게이션

## 🧪 테스트

### 테스트 도구
- **Unit Tests**: Vitest
- **Integration Tests**: Testing Library
- **E2E Tests**: Playwright (계획)
- **Component Tests**: Storybook

### 테스트 커버리지 목표
- 유닛 테스트: > 80%
- 통합 테스트: > 70%
- E2E 테스트: 주요 시나리오 100%

## 🚀 배포 & CI/CD

### 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   (PostgreSQL)  │
│   Next.js 15    │    │   Django 4.x    │    │   + Redis       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 환경 구성
- **Production**: `main` 브랜치 → 자동 배포
- **Staging**: `develop` 브랜치 → 스테이징 환경
- **Development**: 로컬 개발 환경

### 배포 URL
- **Frontend (Production)**: https://your-vercel-domain.vercel.app
- **Backend (Production)**: https://your-railway-backend.railway.app
- **API Documentation**: https://your-railway-backend.railway.app/api/docs/

### GitHub Actions CI/CD 파이프라인

#### 🔄 Backend CI/CD (`backend-ci.yml`)
```bash
# 트리거: vridge_back/** 파일 변경 시
├── Code Quality & Security
│   ├── Black (코드 포맷팅)
│   ├── isort (import 정렬) 
│   ├── flake8 (린팅)
│   ├── Bandit (보안 검사)
│   └── Safety (취약점 검사)
├── Unit Tests & Coverage
│   ├── PostgreSQL/Redis 서비스 실행
│   ├── Django 시스템 체크
│   ├── 테스트 실행 + 커버리지
│   └── Codecov 업로드
├── Deploy to Railway (main 브랜치만)
│   ├── Railway CLI 설치
│   ├── 배포 실행
│   ├── 헬스체크 검증
│   └── Slack 알림
└── Performance Tests (선택적)
    └── Locust 성능 테스트
```

#### 🎨 Frontend CI/CD (`frontend-ci.yml`)
```bash
# 트리거: vridge_front/** 파일 변경 시
├── Code Quality & Type Check
│   ├── TypeScript 타입 검사
│   ├── ESLint 검사
│   ├── Prettier 포맷 검사
│   ├── SCSS 린트 검사
│   └── npm 보안 감사
├── Build & Test
│   ├── Next.js 빌드
│   ├── Unit 테스트 실행
│   ├── Integration 테스트 실행
│   └── 빌드 크기 분석
├── E2E Tests
│   └── Playwright E2E 테스트
├── Deploy to Vercel (main 브랜치만)
│   ├── Vercel CLI 배포
│   ├── 헬스체크 검증
│   ├── 배포 검증
│   └── Slack 알림
└── Performance & Accessibility Audit
    └── Lighthouse CI 실행
```

#### 🔍 Code Quality & Security (`code-quality.yml`)
```bash
# 트리거: 모든 푸시, PR, 주간 스케줄
├── Code Quality Analysis
│   ├── Python: Black, isort, flake8, mypy
│   └── Frontend: TypeScript, ESLint, Stylelint
├── Security Vulnerability Scan
│   ├── Python: Bandit, Safety, Semgrep
│   ├── Node.js: npm audit, audit-ci
│   ├── CodeQL Security Analysis
│   └── SARIF 업로드
├── Dependency & License Check
│   ├── Python: pip-licenses, pipdeptree
│   └── Node.js: license-checker
├── Performance & Complexity Analysis
│   ├── Python: radon, xenon
│   └── Frontend: 번들 분석
└── Generate Summary Report
    └── PR 코멘트 자동 생성
```

### 배포 프로세스 및 품질 게이트

#### 🚪 품질 게이트
모든 배포는 다음 조건을 통과해야 합니다:
- ✅ 모든 테스트 통과 (커버리지 > 70%)
- ✅ 코드 품질 검사 통과 (린팅, 포맷팅)
- ✅ 보안 취약점 없음 (High/Critical)
- ✅ 타입 검사 통과 (TypeScript)
- ✅ 빌드 성공
- ✅ E2E 테스트 통과 (주요 시나리오)

#### 🔄 배포 전략
1. **Feature 브랜치** → PR 생성 → 코드 리뷰 → 자동 테스트
2. **Develop 브랜치** → 스테이징 배포 → 통합 테스트
3. **Main 브랜치** → 프로덕션 배포 → 헬스체크 → 모니터링

### 로컬 배포 및 테스트

#### Backend (Django) 로컬 실행
```bash
cd vridge_back

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집 후

# 데이터베이스 마이그레이션
python manage.py migrate

# 개발 서버 실행
python manage.py runserver 8000
```

#### Frontend (Next.js) 로컬 실행
```bash
cd vridge_front

# 의존성 설치
npm ci

# 환경변수 설정
cp .env.example .env.local
# .env.local 편집 후

# 개발 서버 실행
npm run dev
```

#### 전체 스택 Docker 실행
```bash
# 루트 디렉토리에서
docker-compose up -d

# 서비스 확인
docker-compose ps
```

### 모니터링 및 로그

#### 배포 상태 확인
```bash
# Backend 헬스체크
curl https://your-railway-backend.railway.app/health/

# Frontend 상태 확인  
curl https://your-vercel-domain.vercel.app/

# 종합 배포 상태 (백엔드에서 실행)
./deployment_health_check.sh
```

#### 로그 모니터링
- **Railway**: Railway 대시보드에서 실시간 로그 확인
- **Vercel**: Vercel 대시보드에서 함수 로그 확인
- **GitHub Actions**: Actions 탭에서 워크플로우 로그 확인

### 환경 변수 설정

#### Backend (.env)
```env
# Django 설정
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-railway-domain.railway.app

# 데이터베이스
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port/0

# 이메일 설정 (SendGrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

#### Frontend (.env.local)
```env
# API 설정
NEXT_PUBLIC_API_BASE_URL=https://your-railway-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-railway-backend.railway.app

# 소셜 로그인
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NEXT_PUBLIC_KAKAO_CLIENT_ID=your-kakao-client-id

# 기타
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=https://your-vercel-domain.vercel.app
```

### 배포 스크립트

#### 수동 배포 (Emergency)
```bash
# Backend 긴급 배포
cd vridge_back
./deploy_railway.sh

# Frontend 긴급 배포  
cd vridge_front
./scripts/vercel-deploy.sh

# 전체 헬스체크
./deployment_health_check.sh
```

## 🤝 기여 가이드

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add some amazing feature'`)
4. 브랜치 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 제보**: [GitHub Issues](https://github.com/your-repo/videoplanet-clean/issues)
- **문서**: [Documentation](https://docs.videoplanet.com)
- **이메일**: support@videoplanet.com

---

**VideoPlanet** - 영상 제작자들의 창의적 협업을 위한 플랫폼