# 백엔드 API 오류 분석 보고서

## 진단 요약

### 1. /api/auth/login/ 500 에러

**근본 원인**: 
- 데이터베이스 스키마와 Django 모델 간 불일치
- `users_user.deletion_reason` 필드가 NOT NULL 제약 조건을 가지고 있어 사용자 생성 시 오류 발생

**현재 상태**:
- ✅ 로컬 환경: 정상 동작 (deletion_reason 필드에 빈 문자열 설정 시)
- ❌ Railway 환경: 500 에러 발생 가능

**해결 방법**:
```python
# users/models.py 수정
deletion_reason = models.CharField(
    max_length=200, 
    default='',  # 기본값 추가
    blank=True, 
    verbose_name="삭제 사유"
)
```

### 2. /api/version/ 404 에러

**원인**: 
- URL 라우팅 설정은 정상이나 Railway 환경에서 접근 문제 가능

**현재 상태**:
- ✅ 로컬 환경: 정상 동작 (200 OK)
- `/api/version/` → 간단한 버전 정보 반환
- `/api/system/version/` → 상세한 시스템 정보 (현재 미사용)

## 즉시 적용 가능한 해결책

### 1단계: 모델 수정
```python
# users/models.py의 26-28번 라인 수정
deletion_reason = models.CharField(
    max_length=200, 
    default='',  # 기본값 추가 (중요!)
    blank=True, 
    verbose_name="삭제 사유"
)
```

### 2단계: Railway 콘솔에서 실행
```bash
# 1. 데이터베이스 업데이트 (PostgreSQL 전용)
python manage.py dbshell
ALTER TABLE users_user ALTER COLUMN deletion_reason SET DEFAULT '';
UPDATE users_user SET deletion_reason = '' WHERE deletion_reason IS NULL;
\q

# 2. 서버 재시작 (Railway는 자동)
```

### 3단계: 환경 변수 확인
Railway 대시보드에서 다음 환경 변수 확인:
- `DJANGO_SETTINGS_MODULE`: `config.settings.railway`
- `DEBUG`: `False` (Production)
- `ALLOWED_HOSTS`: `videoplanet.up.railway.app`
- `DATABASE_URL`: PostgreSQL 연결 문자열

## 테스트 검증

### 로컬 테스트 결과
```bash
# 로그인 테스트 - ✅ 성공
POST /api/auth/login/
Response: 200 OK
{
  "message": "success",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 49,
    "email": "apitest@example.com",
    "nickname": "API Test User"
  }
}

# 버전 확인 - ✅ 성공  
GET /api/version/
Response: 200 OK
{
  "app_name": "VideoPlanet",
  "app_version": "1.0.0",
  "api_version": "1.0",
  "django_version": "4.2.7"
}
```

## Railway 배포 체크리스트

### 배포 전
- [ ] `users/models.py` deletion_reason 필드 수정
- [ ] 로컬 테스트 통과 확인
- [ ] Git 커밋 및 푸시

### 배포 후
- [ ] `/api/health/` 상태 확인
- [ ] `/api/version/` 접근 확인
- [ ] 로그인 API 테스트
- [ ] Railway 로그 모니터링

## 문제 지속 시 추가 조치

### 방법 A: 마이그레이션 리셋
```bash
# Railway 콘솔에서
python manage.py migrate users zero
python manage.py migrate users
```

### 방법 B: 수동 스키마 수정
```sql
-- PostgreSQL
ALTER TABLE users_user 
ALTER COLUMN deletion_reason DROP NOT NULL,
ALTER COLUMN deletion_reason SET DEFAULT '';
```

### 방법 C: 폴백 뷰 확인
`config/auth_fallback.py`에서 Railway 환경 감지 로직 확인:
- Railway 환경에서는 SafeSignIn/SafeSignUp 사용
- 정상적으로 폴백되고 있는지 로그 확인

## 모니터링 포인트

1. **Railway 로그**
   - `INFO auth_fallback Railway environment detected`
   - `ERROR views_signup_safe` 메시지 확인

2. **데이터베이스 연결**
   - PostgreSQL 연결 상태
   - 마이그레이션 상태

3. **API 응답 시간**
   - `/api/health/` < 100ms
   - `/api/auth/login/` < 200ms

## 연락처
문제 지속 시 다음 정보와 함께 보고:
- Railway 배포 ID
- 오류 발생 시각
- 상세 에러 로그
- 테스트한 API 엔드포인트

---
작성일: 2025-08-12
작성자: Backend Lead - Benjamin