# VideoPlanet Backend Railway 배포 가이드

## 📋 개요

이 가이드는 VideoPlanet Django 백엔드를 Railway에 안전하고 효율적으로 배포하기 위한 종합적인 지침서입니다.

## 🚀 배포 준비 상황

### ✅ 완료된 작업
- [x] requirements.txt 최신화 (Django 4.2.7, PostgreSQL, Redis 지원)
- [x] railway.json 최적화 (헬스체크, 재시작 정책 포함)
- [x] Procfile 업데이트 (안정적인 start.sh 사용)
- [x] start.sh 스크립트 (자동 마이그레이션, 강력한 에러 처리)
- [x] 헬스체크 엔드포인트 `/api/health/` 구현
- [x] 환경 변수 설정 가이드
- [x] 배포 자동화 스크립트
- [x] 배포 전 검증 스크립트

## 📁 생성된 배포 파일들

```
vridge_back/
├── railway.json                    # Railway 배포 설정
├── Procfile                        # 프로세스 시작 명령
├── start.sh                        # 안전한 서버 시작 스크립트
├── RAILWAY_ENV_SETUP.md           # 환경 변수 설정 가이드
├── deploy_railway.sh              # 자동 배포 스크립트
├── pre_deploy_check.sh            # 배포 전 검증 스크립트
└── RAILWAY_DEPLOYMENT_GUIDE.md    # 이 파일
```

## 🔧 배포 방법

### 1단계: 사전 준비

#### Railway CLI 설치
```bash
npm install -g @railway/cli
railway login
```

#### 프로젝트 디렉토리 이동
```bash
cd /home/winnmedia/VideoPlanet/vridge_back
```

### 2단계: 배포 전 검증

```bash
# 모든 배포 요구사항 자동 검증
./pre_deploy_check.sh
```

검증 항목:
- ✅ 필수 파일 구조 (manage.py, requirements.txt, Procfile, railway.json)
- ✅ Procfile 올바른 설정 (./start.sh)
- ✅ railway.json 유효성 검증
- ✅ 시작 스크립트 실행 권한
- ✅ 필수 Python 패키지 포함 확인
- ✅ Django 설정 파일 존재
- ✅ 헬스체크 엔드포인트 설정

### 3단계: Railway 프로젝트 설정

#### 새 Railway 프로젝트 생성 (옵션)
```bash
railway new
```

#### 기존 프로젝트에 연결 (옵션)
```bash
railway link
```

#### PostgreSQL 데이터베이스 추가
```bash
railway add --database postgresql
```

#### Redis 서비스 추가 (선택사항)
```bash
railway add --database redis
```

### 4단계: 환경 변수 설정

필수 환경 변수들을 설정합니다:

```bash
# Django 핵심 설정
railway variables set DJANGO_SETTINGS_MODULE=config.settings.railway
railway variables set DEBUG=False
railway variables set SECRET_KEY="<강력한_시크릿_키>"
railway variables set ALLOWED_HOSTS="videoplanet.up.railway.app,*.railway.app,vlanet.net"

# 운영 환경 설정
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

> 💡 **SECRET_KEY 생성**: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`

더 자세한 환경 변수 설정은 `RAILWAY_ENV_SETUP.md`를 참조하세요.

### 5단계: 자동 배포 실행

```bash
./deploy_railway.sh
```

배포 스크립트가 자동으로 다음을 수행합니다:
1. 사전 검사 (Railway CLI, Django 설정)
2. 로컬 테스트 (Django 체크)
3. Railway 프로젝트 연결 확인
4. 환경 변수 검증
5. 서비스 확인 (PostgreSQL, Redis)
6. 배포 실행
7. 배포 상태 모니터링
8. 배포 후 검증 (헬스체크, API 엔드포인트)

## ⚙️ 기술적 세부사항

### Railway 배포 설정 (railway.json)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "./start.sh",
    "restartPolicyType": "ON_FAILURE", 
    "restartPolicyMaxRetries": 3,
    "healthcheckPath": "/api/health/",
    "healthcheckTimeout": 60,
    "replicas": 1
  },
  "environments": {
    "production": {
      "variables": {
        "DJANGO_SETTINGS_MODULE": "config.settings.railway",
        "PYTHONPATH": "/app",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 시작 스크립트 (start.sh) 주요 기능

1. **강력한 데이터베이스 연결 검증**
   - 10회까지 재시도 (Railway 환경 특화)
   - PostgreSQL 연결 상태 진단
   - 8초 간격으로 재시도

2. **자동 마이그레이션 시스템**
   - 마이그레이션 상태 확인
   - 개별 앱별 마이그레이션 처리
   - 중요 필드 존재 여부 검증
   - 수동 스키마 복구 로직

3. **프로덕션 최적화**
   - Gunicorn 서버 (2 workers, 4 threads)
   - 120초 타임아웃
   - 프리로드 모드
   - 요청 제한 (1000 + 50 jitter)

### 헬스체크 엔드포인트

```python
# /api/health/ 엔드포인트
def ultra_fast_health(request):
    return HttpResponse("OK", status=200, content_type="text/plain")
```

Railway가 60초마다 이 엔드포인트를 호출하여 서비스 상태를 확인합니다.

## 📊 배포 후 확인사항

### 1. 서비스 상태 확인
```bash
railway ps
railway logs
```

### 2. 헬스체크 테스트
```bash
curl https://your-service.up.railway.app/api/health/
# 응답: OK (200)
```

### 3. API 엔드포인트 테스트
```bash
# 기본 API들 (401 Unauthorized는 정상 - 인증이 필요함을 의미)
curl https://your-service.up.railway.app/api/users/
curl https://your-service.up.railway.app/api/projects/
curl https://your-service.up.railway.app/api/calendar/
curl https://your-service.up.railway.app/api/invitations/
curl https://your-service.up.railway.app/api/feedbacks/
```

### 4. 데이터베이스 연결 확인
```bash
railway run python manage.py dbshell --command="SELECT version();"
```

### 5. CORS 설정 확인
브라우저에서 프론트엔드(https://vlanet.net)가 API에 정상 접근하는지 확인

## 🔧 트러블슈팅

### 자주 발생하는 문제들

#### 1. 서버 시작 실패
**증상**: 서비스가 CRASHED 상태
**해결**:
```bash
railway logs  # 에러 로그 확인
```
- 환경 변수 누락 → `RAILWAY_ENV_SETUP.md` 참조
- 데이터베이스 연결 실패 → PostgreSQL 서비스 활성화 확인

#### 2. 헬스체크 실패
**증상**: 서비스가 반복적으로 재시작
**해결**:
```bash
# 헬스체크 경로 수동 테스트
railway run python manage.py shell -c "
from django.test import Client
print(Client().get('/api/health/').status_code)
"
```

#### 3. 마이그레이션 오류
**증상**: 시작 시 마이그레이션 실패
**해결**:
```bash
# 수동 마이그레이션 실행
railway run python manage.py migrate --verbosity=2
railway run python manage.py showmigrations
```

#### 4. CORS 에러
**증상**: 프론트엔드에서 API 호출 실패
**해결**:
- `CORS_ALLOWED_ORIGINS` 환경 변수에 프론트엔드 도메인 추가
- `CSRF_TRUSTED_ORIGINS`도 함께 설정

#### 5. Static 파일 404
**증상**: CSS, JS 파일 로드 실패
**해결**:
```bash
railway run python manage.py collectstatic --noinput
```

### Railway 명령어 참고

```bash
# 서비스 상태 확인
railway ps

# 실시간 로그 확인
railway logs

# 환경 변수 목록
railway variables

# 서비스 재시작
railway restart

# 도메인 정보
railway domain

# 수동 명령 실행
railway run <command>
```

## 🔒 보안 고려사항

### 프로덕션 보안 체크리스트
- [x] DEBUG=False 설정
- [x] SECRET_KEY 암호화된 값 사용
- [x] ALLOWED_HOSTS 제한적 설정
- [x] CORS 설정으로 도메인 제한
- [x] HTTPS 강제 리다이렉트
- [x] 보안 쿠키 설정
- [x] SQL 인젝션 방지 (Django ORM)
- [ ] Rate Limiting 설정 (추후 개선)
- [ ] API 키 관리 시스템 (추후 개선)

## 📈 모니터링 및 로그

### Railway 대시보드
- CPU, 메모리, 네트워크 사용량 모니터링
- 배포 히스토리 및 롤백 기능
- 실시간 로그 및 메트릭

### 로그 관리
```bash
# 최근 로그 확인
railway logs --tail 100

# 실시간 로그 스트리밍
railway logs --follow

# 특정 시간 범위 로그
railway logs --since 1h
```

## 🚀 CI/CD 파이프라인 (미래 계획)

### GitHub Actions 연동
```yaml
# .github/workflows/deploy-railway.yml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up --detach
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 📞 지원 및 문의

### Railway 지원
- 공식 문서: https://docs.railway.app
- 커뮤니티: https://discord.gg/railway
- 지원팀: support@railway.app

### 프로젝트 관련
- GitHub 이슈: https://github.com/winnmedia/Vlanet_v2.0/issues
- API 문서: https://videoplanet.up.railway.app/api/docs/

---

## 📝 배포 체크리스트

### 배포 전
- [ ] `./pre_deploy_check.sh` 실행하여 모든 항목 통과
- [ ] Railway CLI 로그인 및 프로젝트 연결
- [ ] 필수 환경 변수 설정 완료
- [ ] PostgreSQL 서비스 연결 확인

### 배포 중
- [ ] `./deploy_railway.sh` 실행
- [ ] 배포 로그 모니터링
- [ ] 서비스 시작 확인

### 배포 후  
- [ ] 헬스체크 엔드포인트 응답 확인 (200 OK)
- [ ] 기본 API 엔드포인트 접근 확인
- [ ] 프론트엔드에서 API 연동 테스트
- [ ] 데이터베이스 마이그레이션 완료 확인
- [ ] 에러 로그 확인 및 이슈 해결

---

**마지막 업데이트**: 2025-08-11  
**작성자**: Emily (CI/CD Engineer)  
**버전**: 1.0.0