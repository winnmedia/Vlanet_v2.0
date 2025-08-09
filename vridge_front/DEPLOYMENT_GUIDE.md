# VideoPlanet 2.0 배포 가이드

## 🚀 빠른 시작

### 1. GitHub 리포지토리 생성
```bash
# GitHub에서 vlanet_2.0 리포지토리 생성 후
git remote add origin https://github.com/YOUR_USERNAME/vlanet_2.0.git
git push -u origin main
```

### 2. Vercel 배포 (프론트엔드)
1. [Vercel](https://vercel.com) 접속 후 로그인
2. "Import Git Repository" 클릭
3. `vlanet_2.0` 리포지토리 선택
4. 프레임워크: Next.js 자동 감지
5. 환경변수 설정:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR_RAILWAY_URL.up.railway.app
   NEXT_PUBLIC_APP_NAME=VideoPlanet
   NEXT_PUBLIC_APP_VERSION=2.0.0
   ```
6. Deploy 클릭

### 3. Railway 배포 (백엔드)
1. [Railway](https://railway.app) 접속 후 로그인
2. "New Project" → "Deploy from GitHub repo"
3. `vlanet_2.0` 리포지토리 선택
4. 서비스 설정:
   - 경로: `/vridge_back`
   - Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. 환경변수 설정:
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=.up.railway.app
   DJANGO_SETTINGS_MODULE=config.settings.railway
   ```
6. Deploy 클릭

## 📋 환경변수 설정

### Vercel (프론트엔드)
```env
# 필수
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
NEXT_PUBLIC_APP_NAME=VideoPlanet
NEXT_PUBLIC_APP_VERSION=2.0.0

# 선택
NEXT_PUBLIC_GA_ID=GA-XXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Railway (백엔드)
```env
# Django 설정
SECRET_KEY=your-very-secret-key
DEBUG=False
ALLOWED_HOSTS=.up.railway.app,.vlanet.net

# 데이터베이스
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (캐시)
REDIS_URL=redis://user:pass@host:6379

# 이메일
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AI API Keys (선택)
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=sk-...
```

## 🔧 배포 전 체크리스트

### 프론트엔드
- [ ] 빌드 테스트: `npm run build`
- [ ] 린트 체크: `npm run lint`
- [ ] 타입 체크: `npm run type-check`
- [ ] 환경변수 확인
- [ ] API URL 설정 확인

### 백엔드
- [ ] 마이그레이션: `python manage.py migrate`
- [ ] 정적파일: `python manage.py collectstatic`
- [ ] 슈퍼유저 생성: `python manage.py createsuperuser`
- [ ] 테스트 실행: `python manage.py test`
- [ ] requirements.txt 확인

## 🌐 도메인 연결

### Vercel 커스텀 도메인
1. Vercel 프로젝트 → Settings → Domains
2. 도메인 추가 (예: vlanet.net)
3. DNS 설정:
   ```
   A Record: @ → 76.76.21.21
   CNAME: www → cname.vercel-dns.com
   ```

### Railway 커스텀 도메인
1. Railway 서비스 → Settings → Domains
2. 도메인 추가 (예: api.vlanet.net)
3. DNS 설정:
   ```
   CNAME: api → your-app.up.railway.app
   ```

## 🔄 CI/CD 설정

### GitHub Actions (자동 배포)
`.github/workflows/deploy.yml` 파일이 이미 설정되어 있습니다:
- main 브랜치 푸시 시 자동 배포
- PR 생성 시 자동 테스트
- 매일 정기 헬스체크

### 시크릿 설정
GitHub 리포지토리 → Settings → Secrets:
- `VERCEL_TOKEN`: Vercel API 토큰
- `RAILWAY_TOKEN`: Railway API 토큰

## 🐛 트러블슈팅

### Vercel 빌드 실패
```bash
# 로컬에서 빌드 테스트
npm run build

# 일반적인 문제:
# - Node 버전 확인 (18.x 이상)
# - 환경변수 누락
# - 타입 에러
```

### Railway 배포 실패
```bash
# 로컬에서 테스트
python manage.py check --deploy

# 일반적인 문제:
# - requirements.txt 누락 패키지
# - 데이터베이스 연결 실패
# - 포트 설정 오류
```

### CORS 에러
백엔드 `settings.py`에서 CORS 설정 확인:
```python
CORS_ALLOWED_ORIGINS = [
    "https://vlanet.net",
    "https://www.vlanet.net",
    "http://localhost:3000",
]
```

## 📊 모니터링

### 헬스체크 엔드포인트
- 프론트엔드: `https://vlanet.net/api/health`
- 백엔드: `https://api.vlanet.net/api/health/`

### 로그 확인
- Vercel: Dashboard → Functions → Logs
- Railway: Dashboard → Service → Logs

## 🔐 보안 체크리스트

- [ ] 환경변수에 시크릿 저장
- [ ] HTTPS 강제 사용
- [ ] CORS 올바른 설정
- [ ] Rate Limiting 설정
- [ ] SQL Injection 방어
- [ ] XSS 방어
- [ ] CSRF 토큰 활성화

## 📞 지원

문제 발생 시:
1. [GitHub Issues](https://github.com/YOUR_USERNAME/vlanet_2.0/issues)
2. [Vercel Support](https://vercel.com/support)
3. [Railway Support](https://railway.app/support)

---
*Last Updated: 2025-08-10*
*Version: 2.0.0*