# 🚨 Railway 대시보드에서 직접 수정하기

## 1단계: Railway 대시보드 접속
1. https://railway.app 로그인
2. **VideoPlane** 프로젝트 선택

## 2단계: 서비스 재시작
1. **Deployments** 탭 클릭
2. 오른쪽 상단 **⋮** (점 3개) 메뉴 클릭
3. **Restart** 선택

## 3단계: 환경 변수 확인/추가
**Variables** 탭에서 다음 변수 확인:

```
DJANGO_SETTINGS_MODULE=config.settings.railway
SECRET_KEY=(자동 생성된 값 유지)
DATABASE_URL=(자동 설정된 값 유지)
DEBUG=False
ALLOWED_HOSTS=videoplanet.up.railway.app
CORS_ALLOWED_ORIGINS=https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app,https://vlanet.net
```

없는 변수는 **New Variable** 버튼으로 추가

## 4단계: 데이터베이스 수정
**Settings** → **Run a Command** 에서:

```bash
python manage.py migrate users --fake
```

또는

```bash
python fix_railway_db.py
```

## 5단계: 로그 확인
**Observability** → **Logs** 에서 에러 확인

빨간색 에러가 있다면:
- `deletion_reason` 관련 에러 → 4단계 재실행
- CORS 에러 → 3단계 환경 변수 확인

## 6단계: 테스트
브라우저에서:
1. https://videoplanet.up.railway.app/api/health/ 접속
2. {"status":"ok"} 응답 확인

## 문제 지속 시
**Settings** → **Danger Zone** → **Redeploy** 클릭

## 긴급 연락
Railway Discord: https://discord.gg/railway