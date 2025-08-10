# Railway 환경변수 설정 가이드 (긴급 수정 버전)

## 🚨 500 에러 해결을 위한 필수 환경변수

Railway 대시보드에서 다음 환경변수를 **반드시** 설정해주세요:

### 1. Django 핵심 설정 (필수)
```
DJANGO_SETTINGS_MODULE=config.settings.railway
SECRET_KEY=django-insecure-very-long-random-string-at-least-50-characters-replace-this
DEBUG=True  # 문제 해결 후 False로 변경
```

### 2. 데이터베이스 설정 (필수)
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```
- Railway PostgreSQL 서비스를 추가하면 자동으로 설정됩니다
- **중요**: PostgreSQL 서비스가 실행 중인지 확인하세요

### 3. CORS 설정 (필수)
```
CORS_ALLOWED_ORIGINS=https://vlanet.net,https://www.vlanet.net,https://videoplanet-seven.vercel.app
FRONTEND_URL=https://vlanet.net
```

### 4. Redis 설정 (선택사항 - 없어도 작동)
```
REDIS_URL=redis://default:password@host:port
```
- Railway Redis 서비스를 추가하면 자동으로 설정됩니다
- 없으면 데이터베이스 캐시를 사용합니다

### 5. 이메일 설정 (선택사항)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@videoplanet.com
```

## 🔧 Railway에서 환경변수 설정 방법

1. **Railway 대시보드 접속**: https://railway.app
2. **VideoPlanet 프로젝트 선택**
3. **Variables 탭 클릭** (Settings가 아닌 Variables)
4. **Raw Editor 모드로 전환** (오른쪽 상단)
5. **아래 환경변수 복사 후 붙여넣기**:

```env
DJANGO_SETTINGS_MODULE=config.settings.railway
SECRET_KEY=django-insecure-very-long-random-string-at-least-50-characters-replace-this
DEBUG=True
FRONTEND_URL=https://vlanet.net
CORS_ALLOWED_ORIGINS=https://vlanet.net,https://www.vlanet.net
```

6. **Save 버튼 클릭**
7. **자동 재배포 대기** (약 2-3분)

## 📊 상태 확인 방법

### 1. 헬스체크 (기본)
```
https://videoplanet.up.railway.app/api/health/
```

### 2. 디버그 상태 (DEBUG=True일 때만)
```
https://videoplanet.up.railway.app/api/debug/status/
```

### 3. 테스트 API 호출
```bash
# 이메일 중복 확인 테스트
curl -X POST https://videoplanet.up.railway.app/api/auth/check-email/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## 🚨 500 에러 트러블슈팅

### 1. SECRET_KEY 확인
- 최소 50자 이상의 랜덤 문자열 사용
- 특수문자 포함 가능 (따옴표 제외)

### 2. DATABASE_URL 확인
- PostgreSQL 서비스가 활성화되어 있는지 확인
- Railway가 자동으로 설정한 DATABASE_URL 사용

### 3. 로그 확인
- Railway 대시보드 → Deployments → View Logs
- 구체적인 에러 메시지 확인

### 4. 마이그레이션 실행 확인
- 배포 로그에서 "마이그레이션 실행" 메시지 확인
- 실패 시 수동으로 실행 필요

## 🔍 일반적인 문제와 해결

### "Module not found" 에러
```
pip install -r requirements.txt
```

### "CORS policy" 에러
```
CORS_ALLOWED_ORIGINS에 프론트엔드 도메인 추가
https:// 포함하여 정확히 입력
```

### "Database connection refused"
```
PostgreSQL 서비스 재시작
DATABASE_URL 형식 확인
```

### "CSRF token missing"
```
CSRF_TRUSTED_ORIGINS 환경변수 추가
프론트엔드와 백엔드 도메인 모두 포함
```

## ✅ 최종 체크리스트

- [ ] DJANGO_SETTINGS_MODULE = config.settings.railway
- [ ] SECRET_KEY 설정 (50자 이상)
- [ ] DATABASE_URL 자동 설정 확인
- [ ] CORS_ALLOWED_ORIGINS에 프론트엔드 도메인 추가
- [ ] 헬스체크 URL 응답 확인
- [ ] 로그에서 에러 메시지 확인
- [ ] 회원가입 API 테스트

---
최종 업데이트: 2025-08-10
문제 발생 시 로그를 확인하세요!