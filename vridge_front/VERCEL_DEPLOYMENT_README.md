# VideoPlanet Vercel 배포 가이드

이 문서는 VideoPlanet 프론트엔드를 Vercel에 안전하고 효율적으로 배포하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 자동 배포 (권장)

```bash
# 프로덕션 배포
./scripts/vercel-deploy.sh

# 프리뷰 배포
./scripts/vercel-deploy.sh --preview

# 개발 환경 배포
./scripts/vercel-deploy.sh --dev
```

### 2. 수동 배포

```bash
# 환경 변수 검증
npm run validate-vercel-config

# 빌드 테스트
npm run build

# Vercel 배포
vercel --prod  # 프로덕션
vercel         # 프리뷰
```

## 📋 배포 전 체크리스트

### 필수 사항
- [ ] Node.js 18.0.0+ 설치됨
- [ ] Vercel CLI 설치됨 (`npm i -g vercel`)
- [ ] Git 커밋 완료 (프로덕션 배포 시)
- [ ] 환경 변수 설정 완료
- [ ] 빌드 테스트 성공

### 권장 사항
- [ ] 린트 검사 통과
- [ ] TypeScript 타입 체크 통과
- [ ] 테스트 케이스 통과
- [ ] API 연결성 확인

## 🔧 설정 파일 설명

### vercel.json
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install --legacy-peer-deps",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://videoplanet.up.railway.app",
    "NODE_ENV": "production"
  }
}
```

### .vercelignore
불필요한 파일들을 배포에서 제외하여 빌드 시간 단축:
- 테스트 파일
- 문서 파일
- 개발 전용 설정
- 로그 파일

## 🌍 환경 변수 설정

### 필수 환경 변수
```bash
NEXT_PUBLIC_API_URL=https://videoplanet.up.railway.app
NEXT_PUBLIC_APP_NAME=VideoPlanet
NODE_ENV=production
```

### 권장 환경 변수
```bash
NEXT_PUBLIC_APP_URL=https://vlanet.net
NEXTAUTH_URL=https://vlanet.net
NEXTAUTH_SECRET=your-secure-secret-key
```

### 환경 변수 검증
```bash
# 환경 변수 검증
npm run check-env

# 연결성 포함 검증
node scripts/validate-vercel-env.js --check-connectivity

# 환경 변수 템플릿 생성
node scripts/validate-vercel-env.js --template
```

## 📊 배포 타입별 설정

### Production (프로덕션)
- **브랜치**: main/master만 허용
- **도메인**: https://vlanet.net
- **환경**: NODE_ENV=production
- **특징**: 미커밋 변경사항 불허, 엄격한 검증

### Preview (프리뷰)
- **브랜치**: 모든 브랜치 허용
- **도메인**: vercel-*.vercel.app
- **환경**: NODE_ENV=production
- **특징**: 기능 테스트용, PR 검토용

### Development (개발)
- **브랜치**: 개발 브랜치
- **도메인**: dev-*.vercel.app
- **환경**: NODE_ENV=development
- **특징**: 개발 중 실시간 테스트

## 🔍 헬스 체크

배포 후 자동으로 실행되는 헬스 체크 항목:

### 프론트엔드 엔드포인트
- [ ] 홈페이지 (/)
- [ ] 로그인 페이지 (/login)
- [ ] 회원가입 페이지 (/signup)
- [ ] 대시보드 (/dashboard)
- [ ] 프로젝트 목록 (/projects)

### 백엔드 API 엔드포인트
- [ ] API 상태 체크 (/api/health/)
- [ ] 사용자 프로필 (/api/users/profile/)

### 수동 헬스 체크
```bash
# 배포된 사이트 헬스 체크
node scripts/vercel-health-check.js

# 상세 리포트 생성
node scripts/vercel-health-check.js --report
```

## ⚡ 빌드 최적화

### 자동 최적화 설정

1. **Tree Shaking**: 사용하지 않는 코드 자동 제거
2. **Code Splitting**: 페이지별 번들 분리
3. **Image Optimization**: 이미지 자동 최적화 (WebP, AVIF)
4. **CSS Optimization**: CSS 압축 및 중복 제거

### 수동 최적화

```bash
# 번들 분석
ANALYZE=true npm run build

# 의존성 최적화
npm audit fix
npm update

# 캐시 정리
npm run clean
```

### 성능 모니터링

```bash
# 빌드 시간 측정
time npm run build

# 번들 크기 확인
npm run build && du -sh .next/

# Lighthouse 성능 측정
npx lighthouse https://vlanet.net --output html
```

## 🔒 보안 설정

### 보안 헤더 (next.config.js)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin

### 환경 변수 보안
- 민감 정보는 Vercel 대시보드에서 설정
- .env.local 파일은 Git에서 제외
- 프로덕션 시크릿은 별도 관리

## 📱 모바일 최적화

### PWA 설정
- Service Worker 구성
- 오프라인 캐싱
- 앱 매니페스트

### 반응형 디자인
- Tailwind CSS 반응형 클래스
- 모바일 우선 설계
- 터치 친화적 UI

## 🐛 문제 해결

### 일반적인 오류

1. **빌드 실패**
   ```bash
   # 의존성 재설치
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   
   # TypeScript 오류 무시 (임시)
   # next.config.js에서 typescript.ignoreBuildErrors: true
   ```

2. **환경 변수 오류**
   ```bash
   # 환경 변수 확인
   npm run check-env
   
   # Vercel 환경 변수 동기화
   vercel env pull .env.local
   ```

3. **API 연결 오류**
   ```bash
   # API 서버 상태 확인
   curl https://videoplanet.up.railway.app/api/health/
   
   # 네트워크 연결 테스트
   node scripts/validate-vercel-env.js --check-connectivity
   ```

### 디버깅 명령어

```bash
# 상세 빌드 로그
npm run build -- --debug

# Vercel 배포 로그 확인
vercel logs

# 로컬에서 프로덕션 빌드 테스트
npm run build && npm start
```

## 📈 모니터링 및 분석

### Vercel 대시보드
- 배포 상태 모니터링
- 성능 메트릭 확인
- 에러 로그 분석
- 트래픽 통계

### 외부 모니터링 도구
- Google Analytics (설정됨)
- Sentry 에러 추적 (선택사항)
- Lighthouse CI (자동 성능 측정)

## 🔄 CI/CD 설정

### GitHub Actions (선택사항)
```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: ./scripts/vercel-deploy.sh --preview
```

### 자동 배포 트리거
- main 브랜치 푸시 → 프로덕션 배포
- PR 생성 → 프리뷰 배포
- 개발 브랜치 푸시 → 개발 배포

## 📞 지원 및 문의

### 배포 관련 문제
1. 배포 로그 확인: `vercel logs`
2. 헬스 체크 실행: `node scripts/vercel-health-check.js --report`
3. 환경 변수 검증: `npm run check-env`

### 긴급 상황 대응
```bash
# 이전 배포로 롤백
vercel rollback

# 배포 일시 중단
vercel alias rm vlanet.net

# 긴급 핫픽스 배포
./scripts/vercel-deploy.sh --skip-health-check
```

---

## 📝 버전 히스토리

- **v2.1.27** (2025-08-11): Vercel 배포 자동화 스크립트 추가
- **v2.1.26** (2025-08-10): Next.js 15 업그레이드 및 최적화
- **v2.1.25** (2025-08-09): QA 테스트 완료, 88.9% 성공률

---

*이 문서는 VideoPlanet 프로젝트의 안전한 배포를 위해 작성되었습니다. 배포 전 반드시 체크리스트를 확인해 주세요.*