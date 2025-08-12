# Railway 배포 최종 가이드

## 1. 필수 환경 변수 설정 (Railway 대시보드에서)

```bash
# Django 필수 설정
DJANGO_SETTINGS_MODULE=config.settings.railway
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app,localhost,127.0.0.1

# 데이터베이스 설정 (Railway에서 자동 제공)
DATABASE_URL=postgresql://...

# CORS 설정
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
CORS_ALLOW_ALL_ORIGINS=False

# 정적 파일 설정
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles

# Railway 특정 설정
RAILWAY_ENVIRONMENT=production
PORT=8000  # Railway가 자동으로 설정함
```

## 2. 배포 파일 구조

현재 설정된 파일들:

### railway.json
- Railway의 메인 설정 파일
- 빌드 및 배포 명령 정의
- 스타트 명령: `bash railway_start.sh`

### railway_start.sh
- 실제 서버 시작 스크립트
- 마이그레이션 및 정적 파일 수집 자동화
- Gunicorn 서버 실행

### Procfile
- Railway의 대체 배포 메커니즘
- railway.json이 없을 경우 사용됨

### nixpacks.toml
- Railway의 빌드 시스템 설정
- Python 및 PostgreSQL 패키지 설치

## 3. 헬스체크 엔드포인트

- **URL**: `/health/`
- **메소드**: GET
- **응답**: `{"status": "healthy", "service": "videoplanet-backend"}`
- **상태 코드**: 200

## 4. 배포 체크리스트

### 배포 전 확인사항:
- [ ] 모든 환경 변수가 Railway에 설정되었는가?
- [ ] DATABASE_URL이 올바르게 설정되었는가?
- [ ] ALLOWED_HOSTS에 Railway 앱 도메인이 포함되었는가?
- [ ] SECRET_KEY가 안전한 값으로 설정되었는가?

### 배포 후 확인사항:
- [ ] https://your-app.up.railway.app/health/ 접속 확인
- [ ] 마이그레이션이 성공적으로 실행되었는가?
- [ ] 정적 파일이 제대로 제공되는가?
- [ ] 로그에 에러가 없는가?

## 5. 일반적인 문제 해결

### 문제: 503 Service Unavailable
**해결책**:
1. Railway 로그 확인
2. 환경 변수 확인 (특히 DJANGO_SETTINGS_MODULE)
3. 데이터베이스 연결 확인

### 문제: Static files not found
**해결책**:
1. STATIC_ROOT 설정 확인
2. collectstatic 명령 실행 여부 확인
3. WhiteNoise 미들웨어 활성화 확인

### 문제: Database connection error
**해결책**:
1. DATABASE_URL 환경 변수 확인
2. PostgreSQL 애드온 활성화 확인
3. 마이그레이션 실행 확인

## 6. 모니터링

Railway 대시보드에서 확인할 사항:
- **Deployments**: 배포 상태 및 로그
- **Metrics**: CPU, 메모리 사용량
- **Logs**: 실시간 애플리케이션 로그
- **Environment**: 환경 변수 설정

## 7. 롤백 절차

문제 발생 시:
1. Railway 대시보드에서 이전 배포로 롤백
2. 또는 Git에서 이전 커밋으로 되돌리고 재배포

## 마지막 업데이트: 2025-08-12