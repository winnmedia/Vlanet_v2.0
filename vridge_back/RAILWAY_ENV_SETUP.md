# Railway 환경 변수 설정 가이드

## 필수 환경 변수 (Required Variables)

### 1. Django 핵심 설정
```bash
DJANGO_SETTINGS_MODULE=config.settings.railway
DEBUG=False
SECRET_KEY=<강력한_시크릿_키_생성>
ALLOWED_HOSTS=videoplanet.up.railway.app,*.railway.app,vlanet.net
```

### 2. 데이터베이스 설정 (Railway PostgreSQL)
```bash
DATABASE_URL=postgresql://username:password@host:port/database_name
# Railway가 자동으로 제공하는 PostgreSQL DATABASE_URL 사용
```

### 3. Redis 설정
```bash
REDIS_URL=redis://username:password@host:port/0
# Railway Redis 서비스의 URL 사용
```

### 4. 기본 운영 환경 설정
```bash
PYTHONUNBUFFERED=1
PYTHONPATH=/app
PORT=8000
ENVIRONMENT=production
```

## 선택적 환경 변수 (Optional Variables)

### 5. Email 설정 (SendGrid 사용)
```bash
SENDGRID_API_KEY=<sendgrid_api_key>
DEFAULT_FROM_EMAIL=noreply@vlanet.net
```

### 6. AI 서비스 API 키
```bash
OPENAI_API_KEY=<openai_api_key>
GOOGLE_API_KEY=<google_gemini_api_key>
TWELVELABS_API_KEY=<twelvelabs_api_key>
```

### 7. 소셜 로그인 (Google OAuth)
```bash
GOOGLE_OAUTH2_CLIENT_ID=<google_client_id>
GOOGLE_OAUTH2_CLIENT_SECRET=<google_client_secret>
```

### 8. 파일 스토리지 (AWS S3)
```bash
AWS_ACCESS_KEY_ID=<aws_access_key>
AWS_SECRET_ACCESS_KEY=<aws_secret_key>
AWS_STORAGE_BUCKET_NAME=<bucket_name>
AWS_S3_REGION_NAME=ap-northeast-2
USE_S3=True
```

### 9. 보안 설정
```bash
CORS_ALLOWED_ORIGINS=https://vlanet.net,https://www.vlanet.net
CSRF_TRUSTED_ORIGINS=https://vlanet.net,https://www.vlanet.net,https://videoplanet.up.railway.app
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 10. 캐싱 및 성능
```bash
CACHE_TIMEOUT=300
MAX_UPLOAD_SIZE=104857600  # 100MB
```

## Railway CLI를 통한 환경 변수 설정

### 1. Railway CLI 설치 및 로그인
```bash
npm install -g @railway/cli
railway login
```

### 2. 프로젝트에 연결
```bash
cd /home/winnmedia/VideoPlanet/vridge_back
railway link
```

### 3. 환경 변수 일괄 설정
```bash
# 필수 변수들 설정
railway variables set DJANGO_SETTINGS_MODULE=config.settings.railway
railway variables set DEBUG=False
railway variables set SECRET_KEY="<생성된_시크릿_키>"
railway variables set ALLOWED_HOSTS="videoplanet.up.railway.app,*.railway.app,vlanet.net"
railway variables set PYTHONUNBUFFERED=1
railway variables set PYTHONPATH=/app
railway variables set ENVIRONMENT=production

# 보안 설정
railway variables set CORS_ALLOWED_ORIGINS="https://vlanet.net,https://www.vlanet.net"
railway variables set CSRF_TRUSTED_ORIGINS="https://vlanet.net,https://www.vlanet.net,https://videoplanet.up.railway.app"
railway variables set SECURE_SSL_REDIRECT=True
railway variables set SESSION_COOKIE_SECURE=True
railway variables set CSRF_COOKIE_SECURE=True
```

### 4. 데이터베이스 및 Redis 서비스 추가
```bash
# PostgreSQL 서비스 추가
railway add --database postgresql

# Redis 서비스 추가  
railway add --database redis
```

## Django SECRET_KEY 생성 방법

### Python을 이용한 SECRET_KEY 생성
```bash
python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
key = ''.join(secrets.choice(alphabet) for _ in range(50))
print(f'SECRET_KEY={key}')
"
```

## 환경 변수 확인 및 테스트

### 1. Railway 대시보드에서 확인
- Railway 프로젝트 대시보드 → Variables 탭에서 모든 환경 변수 확인

### 2. 로컬에서 Railway 환경 변수 테스트
```bash
railway run python manage.py check --deploy
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

### 3. 배포 상태 확인
```bash
railway logs
railway ps
```

## 중요 참고사항

### 보안 주의사항
1. SECRET_KEY는 절대 공개 저장소에 커밋하지 말 것
2. API 키들은 Railway Variables에서만 관리
3. DEBUG=False로 프로덕션에서 설정 필수
4. ALLOWED_HOSTS에 정확한 도메인만 포함

### Railway 특화 설정
1. PORT는 Railway가 자동으로 할당 (보통 $PORT 환경변수 사용)
2. DATABASE_URL과 REDIS_URL은 Railway 서비스가 자동 제공
3. 헬스체크 경로는 `/api/health/`로 설정됨
4. 자동 재시작 정책: ON_FAILURE (최대 3회)

### 배포 후 확인사항
1. 헬스체크 엔드포인트 정상 응답 확인
2. 데이터베이스 마이그레이션 완료 확인  
3. Static 파일 서빙 정상 확인
4. API 엔드포인트 정상 작동 확인
5. CORS 설정 정상 확인 (프론트엔드 연동)

## 트러블슈팅

### 일반적인 문제 해결
1. **서버 시작 실패**: 로그에서 환경 변수 누락 확인
2. **데이터베이스 연결 실패**: DATABASE_URL 형식 확인
3. **CORS 에러**: CORS_ALLOWED_ORIGINS에 프론트엔드 도메인 추가
4. **Static 파일 404**: STATIC_URL과 STATICFILES_DIRS 설정 확인
5. **마이그레이션 실패**: Railway PostgreSQL 서비스 활성화 확인

### Railway 지원 문의
- Railway Support: support@railway.app
- 문서: https://docs.railway.app
- 커뮤니티: https://discord.gg/railway