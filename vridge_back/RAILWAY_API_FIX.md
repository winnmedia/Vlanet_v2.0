# Railway API 오류 해결 가이드

## 문제 진단 결과

### 1. /api/auth/login/ 500 에러
**원인**: 데이터베이스 스키마 불일치
- `users_user.deletion_reason` 필드의 NOT NULL 제약 조건 문제
- 모델 정의와 실제 DB 스키마 불일치

**해결방법**:
1. Railway 콘솔에서 마이그레이션 재실행
2. 또는 데이터베이스 직접 수정

### 2. /api/version/ 404 에러
**원인**: URL 라우팅 설정 문제
- 실제로는 정상 동작하지만 Railway 환경에서 설정 문제 가능

## 즉시 적용 가능한 해결책

### 방법 1: Railway 환경 변수 확인
```bash
# Railway 대시보드에서 확인할 환경 변수
DJANGO_SETTINGS_MODULE=config.settings.railway
DEBUG=False  # Production에서는 False
SECRET_KEY=<your-secret-key>
DATABASE_URL=<postgresql-url>
ALLOWED_HOSTS=videoplanet.up.railway.app
```

### 방법 2: 마이그레이션 명령어 실행
Railway 콘솔에서 다음 명령어 실행:
```bash
# 1. 마이그레이션 파일 생성
python manage.py makemigrations users --name fix_deletion_reason

# 2. 마이그레이션 적용
python manage.py migrate

# 3. 데이터베이스 직접 수정 (PostgreSQL)
python manage.py dbshell
ALTER TABLE users_user ALTER COLUMN deletion_reason DROP NOT NULL;
ALTER TABLE users_user ALTER COLUMN deletion_reason SET DEFAULT '';
```

### 방법 3: 수정된 모델 배포
`users/models.py`에서 deletion_reason 필드 수정:
```python
deletion_reason = models.CharField(
    max_length=200, 
    default='',  # 기본값 추가
    blank=True, 
    verbose_name="삭제 사유"
)
```

## 테스트 스크립트

### 로컬 테스트
```bash
# API 테스트
curl -X POST https://videoplanet.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 버전 확인
curl https://videoplanet.up.railway.app/api/version/
```

### Railway 배포 후 확인사항
1. `/api/health/` - 시스템 상태 확인
2. `/api/version/` - API 버전 정보
3. `/api/auth/login/` - 로그인 기능
4. `/api/auth/signup/` - 회원가입 기능

## 권장 배포 프로세스

1. **데이터베이스 백업**
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

2. **마이그레이션 실행**
   ```bash
   python manage.py migrate --no-input
   ```

3. **정적 파일 수집**
   ```bash
   python manage.py collectstatic --no-input
   ```

4. **서버 재시작**
   Railway는 자동으로 재시작됨

## 모니터링 체크리스트

- [ ] `/api/health/` 엔드포인트 정상 응답 (200 OK)
- [ ] 데이터베이스 연결 정상
- [ ] Redis 캐시 연결 정상 (옵션)
- [ ] 로그인/회원가입 API 정상 동작
- [ ] CORS 설정 정상 (프론트엔드 연동)

## 긴급 롤백 절차

문제 발생 시:
1. Railway 대시보드에서 이전 배포로 롤백
2. 데이터베이스 백업 복원 (필요시)
3. 로그 분석 후 원인 파악

## 관련 파일
- `/vridge_back/config/settings/railway.py` - Railway 설정
- `/vridge_back/users/models.py` - User 모델
- `/vridge_back/config/urls.py` - URL 라우팅
- `/vridge_back/config/auth_fallback.py` - 인증 뷰 폴백