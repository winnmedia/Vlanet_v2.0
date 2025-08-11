# Railway 긴급 수정 가이드

## 🚨 즉시 실행 필요 명령어

### 1. Railway CLI 설치 (이미 설치된 경우 생략)
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### 2. Railway 로그인 및 프로젝트 연결
```bash
railway login
railway link
```

### 3. 데이터베이스 스키마 수정 실행
```bash
# 옵션 1: 안전한 마이그레이션 (권장)
railway run python manage.py migrate users --fake

# 옵션 2: 강제 스키마 수정 (마이그레이션이 실패할 경우)
railway run python -c "
from django.db import connection
with connection.cursor() as cursor:
    # deletion_reason 필드 기본값 추가
    cursor.execute(\"\"\"
        ALTER TABLE users_user 
        ALTER COLUMN deletion_reason 
        SET DEFAULT ''
    \"\"\")
    
    # NULL 값을 빈 문자열로 업데이트
    cursor.execute(\"\"\"
        UPDATE users_user 
        SET deletion_reason = '' 
        WHERE deletion_reason IS NULL
    \"\"\")
    
    print('✅ Database schema fixed successfully!')
"
```

### 4. 서비스 재시작
```bash
railway restart
```

### 5. 상태 확인
```bash
# 헬스체크
curl https://videoplanet.up.railway.app/api/health/

# 로그인 테스트
curl -X POST https://videoplanet.up.railway.app/api/users/login/ \
  -H "Content-Type: application/json" \
  -H "Origin: https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 📝 Railway 대시보드에서 실행하는 방법

1. https://railway.app 접속
2. VideoPlanet 프로젝트 선택
3. Settings → Variables 탭
4. 다음 환경 변수 추가/수정:
   - `CORS_ALLOWED_ORIGINS`: `https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app,https://vlanet.net`
   - `DJANGO_SETTINGS_MODULE`: `config.settings.railway`
5. Deploy 탭에서 "Restart" 클릭

## 🔍 로그 확인
```bash
railway logs --tail
```

## ⚠️ 문제가 지속될 경우

### CORS 긴급 패치 적용
```bash
railway variables set DJANGO_SETTINGS_MODULE=config.cors_emergency_fix
railway up
```

### 데이터베이스 직접 접속
```bash
railway run python manage.py dbshell
```

SQL 직접 실행:
```sql
-- 테이블 구조 확인
\d users_user

-- deletion_reason 필드 수정
ALTER TABLE users_user ALTER COLUMN deletion_reason SET DEFAULT '';
UPDATE users_user SET deletion_reason = '' WHERE deletion_reason IS NULL;

-- 확인
SELECT COUNT(*) FROM users_user WHERE deletion_reason IS NULL;
```

## 📞 지원 요청
문제가 계속될 경우 Railway 지원팀에 문의:
- support@railway.app
- Railway Discord: https://discord.gg/railway