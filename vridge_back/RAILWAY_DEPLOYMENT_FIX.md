# Railway 배포 문제 해결 가이드 (2025-08-12 업데이트)

## 해결된 문제들

### 1. Authentication Import Error (500 Internal Server Error)
**문제**: Railway 환경에서 `views_auth_fixed` 모듈을 찾을 수 없어 500 에러 발생

**원인**: 
- `auth_fallback.py`가 Railway 환경에서도 개발용 뷰를 import하려고 시도
- Import 실패 시 적절한 fallback 처리 부재

**해결책**:
1. Railway 전용 인증 핸들러 생성 (`users/railway_auth.py`)
2. `auth_fallback.py` 개선 - Railway 환경 우선 처리
3. 단계적 fallback 구현 (Railway → Safe → Fallback)

### 2. BaseHTTP 서버 문제
**문제**: 로컬에서 Django 대신 BaseHTTP 서버가 응답

**원인**: 
- `railway_health.py`가 8001 포트를 점유
- Django 서버가 제대로 시작되지 않음

**해결책**:
- 프로세스 정리 및 Django 서버 재시작
- Railway 환경에서만 헬스체크 서버 사용

## 구현된 솔루션

### 1. Railway 전용 인증 핸들러
**파일**: `users/railway_auth.py`
- 최소 의존성으로 안정적인 인증 처리
- Import 에러 방지를 위한 지연 로딩
- Railway 환경 최적화

### 2. 개선된 Auth Fallback
**파일**: `config/auth_fallback.py`
```
Railway 환경 → RailwayLogin/RailwaySignup
    ↓ 실패 시
SafeSignIn/SafeSignUp
    ↓ 실패 시
FallbackView (503 에러)
```

### 3. 향상된 배포 스크립트
**파일**: `railway_start.sh`
- 환경 변수 명시적 설정
- 데이터베이스 연결 테스트
- 캐시 테이블 자동 생성
- Gunicorn 최적화 설정

## Railway 환경 변수 설정 (필수!)

Railway 대시보드에서 다음 환경변수를 설정하세요:

```bash
# Django 핵심 설정
SECRET_KEY=django-insecure-videoplanet-production-key-change-this
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.railway

# 데이터베이스 (Railway PostgreSQL 서비스 추가 시 자동 생성)
# DATABASE_URL=postgresql://...

# Redis (선택사항)
# REDIS_URL=redis://...

# 이메일 설정
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS 설정
CORS_ALLOWED_ORIGINS=https://vlanet.net,https://www.vlanet.net,http://localhost:3000

# AI 서비스 키 (선택사항)
OPENAI_API_KEY=your-openai-key
TWELVE_LABS_API_KEY=your-twelve-labs-key
```

## 배포 체크리스트

### 1. 배포 전 검증
```bash
cd /home/winnmedia/VideoPlanet/vridge_back
./deploy_to_railway.sh
```

### 2. Git 커밋 및 푸시
```bash
git add .
git commit -m "fix: Railway authentication and deployment improvements

- Add Railway-specific auth handlers
- Improve auth_fallback.py with better error handling
- Enhanced railway_start.sh with database checks
- Add deployment verification script"

git push origin main
```

### 3. Railway CLI 배포 (대안)
```bash
railway login
railway up
```

## 모니터링 및 디버깅

### 1. Railway 로그 확인
```bash
railway logs --tail
```

### 2. 헬스체크 확인
```bash
curl https://videoplanet.up.railway.app/api/health/
```

### 3. 인증 API 테스트
```bash
# 로그인 테스트
curl -X POST https://videoplanet.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 회원가입 테스트
curl -X POST https://videoplanet.up.railway.app/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","nickname":"testuser","password":"test1234"}'
```

## 트러블슈팅

### 500 에러 발생 시
1. Railway 로그 확인: `railway logs`
2. `RAILWAY_ENVIRONMENT` 환경 변수 확인
3. `DATABASE_URL` 연결 확인
4. Import 에러 확인

### 로그인 실패 시
1. 데이터베이스 연결 확인
2. User 모델 필드 확인
3. JWT 설정 확인
4. CORS 설정 확인

### 정적 파일 문제
1. `collectstatic` 실행 확인
2. WhiteNoise 설정 확인
3. `STATIC_ROOT` 경로 확인

## 로컬 테스트

### Railway 환경 시뮬레이션
```bash
# Railway 환경 변수 설정
export RAILWAY_ENVIRONMENT=production
export DJANGO_SETTINGS_MODULE=config.settings.railway
export PORT=8001

# Django 서버 시작
python3 manage.py runserver 8001

# 다른 터미널에서 테스트
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 주요 파일 목록

### 인증 관련
- `/users/railway_auth.py` - Railway 전용 인증 핸들러 (NEW)
- `/config/auth_fallback.py` - 인증 뷰 선택 로직 (개선됨)
- `/users/views_signup_safe.py` - Safe 인증 뷰

### 배포 관련
- `/railway_start.sh` - Railway 시작 스크립트 (개선됨)
- `/railway_health.py` - 헬스체크 서버
- `/railway.json` - Railway 설정
- `/deploy_to_railway.sh` - 배포 검증 스크립트 (NEW)

### 설정 관련
- `/config/settings/railway.py` - Railway 전용 설정
- `/config/urls.py` - URL 라우팅

## 성공 지표

✅ 헬스체크 응답: 200 OK
✅ 로그인 API: 정상 작동
✅ 회원가입 API: 정상 작동
✅ JWT 토큰 발급: 성공
✅ CORS 설정: 정상
✅ 정적 파일 서빙: 정상
✅ Import 에러: 해결됨

## 이전 문제와 해결 이력

### 2025-07-31 초기 문제
- Django 앱이 시작되지 않음
- 503 응급 서버로 폴백
- Python 명령어 불일치

### 2025-08-12 추가 문제 및 해결
- Import 에러로 인한 500 에러
- Railway 전용 핸들러로 해결
- 배포 프로세스 개선

---

**최종 업데이트**: 2025-08-12
**작성자**: DevOps/Platform Lead
**상태**: 문제 해결 완료, 배포 준비 완료