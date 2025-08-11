# 🚨 Railway 긴급 복구 가이드

## 현재 상황
- Railway 헬스체크 실패
- Django 서버 시작 불가
- Rate limit 초과 문제

## 즉시 실행 방법

### 옵션 1: Railway 대시보드에서 수동 설정
1. https://railway.app 접속
2. VideoPlane 프로젝트 선택
3. **Settings** → **Deploy** 탭
4. **Start Command** 변경:
   ```
   python minimal_server.py
   ```
5. **Variables** 탭에서 확인:
   - PORT가 설정되어 있는지 확인
   - PYTHONUNBUFFERED=1 추가

6. **Deploy** 탭 → **Restart** 클릭

### 옵션 2: Railway CLI 사용
```bash
railway login
railway link
railway run python minimal_server.py
```

### 옵션 3: Procfile 직접 수정
```bash
echo "web: python minimal_server.py" > Procfile
git add Procfile
git commit -m "Emergency fix"
git push
```

## 테스트
```bash
# 헬스체크
curl https://videoplanet.up.railway.app/api/health/

# 예상 응답
{"status": "ok", "message": "VideoPlanet Backend is running"}
```

## 정상 복구 후
Django 서버가 다시 작동하면:
1. railway.json의 startCommand를 `./start.sh`로 복원
2. Procfile을 `web: ./start.sh`로 복원
3. 정상 배포

## 문제 해결
- 여전히 실패하면 Railway 로그 확인
- Rate limit 문제면 로그 레벨을 ERROR로 설정
- 데이터베이스 문제면 DATABASE_URL 확인