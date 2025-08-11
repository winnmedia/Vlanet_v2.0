# 🚨 Railway 수동 실행 가이드

## 즉시 실행 단계

### 1️⃣ **Railway 웹 콘솔 접속**
1. https://railway.app 접속
2. 로그인
3. **VideoPlane** 프로젝트 선택

### 2️⃣ **Railway CLI 명령어 (터미널에서)**

```bash
# Railway 로그인 (브라우저 열림)
railway login

# 로그인 완료 후 자동 스크립트 재실행
cd /home/winnmedia/VideoPlanet
./railway_fix_auto.sh
```

### 3️⃣ **또는 Railway 웹 콘솔에서 직접 실행**

Railway 대시보드에서:

1. **Settings** → **Environment** → **Shell** 클릭
2. 다음 명령어 붙여넣기:

```python
# Python 쉘에서 실행
from django.db import connection
with connection.cursor() as cursor:
    # deletion_reason 필드 수정
    cursor.execute("""
        ALTER TABLE users_user 
        ALTER COLUMN deletion_reason 
        SET DEFAULT ''
    """)
    
    # NULL 값 업데이트
    cursor.execute("""
        UPDATE users_user 
        SET deletion_reason = '' 
        WHERE deletion_reason IS NULL
    """)
    
    print("✅ Database fixed!")
```

3. **Deploy** 탭 → **Restart** 클릭

### 4️⃣ **환경 변수 확인 (Railway 대시보드)**

**Variables** 탭에서 확인/추가:

```
DJANGO_SETTINGS_MODULE=config.settings.railway
SECRET_KEY=[자동 생성된 값]
DATABASE_URL=[자동 설정됨]
CORS_ALLOWED_ORIGINS=https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app
```

## 🧪 테스트 명령어

```bash
# 1. 헬스체크
curl https://videoplanet.up.railway.app/api/health/

# 2. CORS 테스트
curl -I -X OPTIONS \
  -H "Origin: https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app" \
  https://videoplanet.up.railway.app/api/users/login/

# 3. 로그인 테스트
curl -X POST https://videoplanet.up.railway.app/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 🔍 로그 확인

Railway 대시보드 → **Observability** → **Logs**

또는 CLI:
```bash
railway logs --tail
```

## ⚠️ 문제 지속 시

### Django 마이그레이션 강제 적용
```bash
railway run python manage.py migrate users --fake
railway run python manage.py migrate --run-syncdb
```

### 데이터베이스 직접 접속
```bash
railway run python manage.py dbshell
```

SQL 실행:
```sql
\d users_user;  -- 테이블 구조 확인
SELECT COUNT(*) FROM users_user WHERE deletion_reason IS NULL;  -- NULL 체크
```

## 📞 긴급 지원

- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app