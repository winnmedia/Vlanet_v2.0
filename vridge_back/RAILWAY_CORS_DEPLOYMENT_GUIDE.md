# Railway CORS 문제 해결 및 배포 가이드

## 문제 상황
- **증상**: vlanet.net에서 Railway API 호출 시 CORS 에러 발생
- **에러**: `No 'Access-Control-Allow-Origin' header is present on the requested resource`
- **영향**: 프로덕션 환경에서 로그인 및 모든 API 호출 불가

## 해결 방안 적용

### 1. 미들웨어 순서 최적화 완료
```python
# config/settings_base.py
MIDDLEWARE = [
    "config.middleware.RailwayHealthCheckMiddleware",  
    "corsheaders.middleware.CorsMiddleware",  # CORS를 최상단으로 이동
    "django.middleware.security.SecurityMiddleware",
    # ... 기타 미들웨어
    "config.middleware.GlobalErrorHandlingMiddleware",  # 에러 핸들링을 CORS 뒤로
    "config.cors_middleware.GuaranteedCORSMiddleware",  # 보조 CORS 미들웨어
]
```

### 2. Railway 설정 강화 완료
```python
# config/settings/railway.py
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://vlanet.net",
    "https://www.vlanet.net",
    # ... 기타 허용 오리진
]
CORS_URLS_REGEX = r'^/api/.*$'  # API 경로에 CORS 적용
CORS_REPLACE_HTTPS_REFERER = True  # Railway 프록시 대응
```

### 3. 시작 스크립트 개선 완료
```bash
# railway_start_unified.sh
export CORS_ALLOW_CREDENTIALS=true
export CORS_ALLOWED_ORIGINS="https://vlanet.net,https://www.vlanet.net"

# Gunicorn 프록시 설정 추가
exec gunicorn config.wsgi:application \
    --forwarded-allow-ips="*" \
    --proxy-protocol \
    --proxy-allow-from="*"
```

## 배포 절차

### 1. 로컬 테스트
```bash
# CORS 설정 검증
python3 railway_cors_fix.py

# 로컬 서버 시작
python3 manage.py runserver 8001

# 테스트 요청
curl -X OPTIONS http://localhost:8001/api/users/login/ \
  -H "Origin: https://vlanet.net" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### 2. Git 커밋 및 푸시
```bash
# 변경 사항 커밋
git add -A
git commit -m "fix: Railway CORS configuration for vlanet.net

- Optimize middleware order (CORS first)
- Add GuaranteedCORSMiddleware for error responses
- Configure Gunicorn proxy headers
- Add CORS environment variables to start script"

# Railway로 푸시
git push origin main
```

### 3. Railway 환경 변수 확인
Railway 대시보드에서 다음 환경 변수 확인:
- `DJANGO_SETTINGS_MODULE=config.settings.railway`
- `DEBUG=False`
- `DATABASE_URL` (PostgreSQL 연결 문자열)
- `SECRET_KEY` (프로덕션 시크릿 키)

### 4. 배포 모니터링
```bash
# Railway 로그 확인 (Railway CLI 필요)
railway logs --service=videoplanet

# 헬스체크
curl https://videoplanet.up.railway.app/health/

# CORS 테스트
curl -X OPTIONS https://videoplanet.up.railway.app/api/users/login/ \
  -H "Origin: https://vlanet.net" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

## 검증 체크리스트

### 배포 전
- [ ] 로컬 CORS 테스트 통과
- [ ] railway_cors_fix.py 실행 성공
- [ ] 미들웨어 순서 확인
- [ ] Gunicorn 설정 확인

### 배포 후
- [ ] Railway 빌드 성공
- [ ] 헬스체크 응답 확인
- [ ] OPTIONS 요청 CORS 헤더 확인
- [ ] vlanet.net에서 로그인 테스트
- [ ] 콘솔 에러 없음 확인

## 트러블슈팅

### CORS 헤더가 여전히 없는 경우
1. Railway 로그에서 미들웨어 로딩 확인
2. Gunicorn 워커 재시작 확인
3. Railway 서비스 재배포 시도

### 500 에러 발생 시
1. railway_db_diagnosis.py 실행
2. 데이터베이스 연결 상태 확인
3. GlobalErrorHandlingMiddleware 로그 확인

## 주요 파일 목록
- `/config/settings/railway.py` - Railway 프로덕션 설정
- `/config/settings_base.py` - 기본 설정 (미들웨어 순서)
- `/config/middleware.py` - 미들웨어 구현
- `/config/cors_middleware.py` - CORS 보장 미들웨어
- `/railway_start_unified.sh` - Railway 시작 스크립트
- `/railway_cors_fix.py` - CORS 진단 도구

## 성공 지표
- vlanet.net에서 API 호출 시 CORS 에러 없음
- 모든 API 응답에 Access-Control-Allow-Origin 헤더 포함
- OPTIONS preflight 요청 200 OK 응답
- 로그인 및 인증 정상 작동

## 롤백 계획
문제 발생 시:
1. 이전 커밋으로 롤백: `git revert HEAD`
2. Railway 재배포
3. 기존 CORS 설정으로 복원

---
작성일: 2025-08-12
작성자: Robert (DevOps/Platform Lead)