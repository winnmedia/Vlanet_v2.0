# Railway 배포 체크리스트

## 🚨 즉시 해결 필요 사항

### 1. Railway 서버 상태 확인
현재 서버가 502 Bad Gateway 에러를 반환하고 있습니다. Railway 대시보드에서 다음을 확인하세요:

1. **Railway Dashboard 확인**
   - https://railway.app 로그인
   - videoplanet 프로젝트 선택
   - Deployments 탭에서 최신 배포 상태 확인
   - Logs 탭에서 에러 메시지 확인

2. **필수 환경 변수 확인**
   ```
   SECRET_KEY=<your-secret-key>
   DATABASE_URL=<railway-postgres-url>
   DEBUG=False
   DJANGO_SETTINGS_MODULE=config.settings.railway
   ```

3. **Railway CLI로 로그 확인**
   ```bash
   railway logs --tail 100
   ```

## ✅ 완료된 CORS 수정 사항

### 1. 새로운 CORS 미들웨어 구현
- ✅ `config/cors_solution.py` - 새로운 통합 CORS 미들웨어
  - `OptionsHandlerMiddleware`: OPTIONS 요청 최우선 처리
  - `RailwayCORSMiddleware`: Railway 환경 최적화 CORS 처리

### 2. 설정 파일 업데이트
- ✅ `config/settings_base.py` - 미들웨어 순서 재배치
- ✅ `config/settings/railway.py` - CORS 설정 정리
- ✅ `Procfile` - 불필요한 EOF 라인 제거
- ✅ `railway.json` - 올바른 시작 명령어 확인

### 3. 테스트 도구 생성
- ✅ `test_cors.py` - Python CORS 테스트 스크립트
- ✅ `cors_test.html` - 브라우저 CORS 테스트 페이지
- ✅ `core/management/commands/check_cors.py` - Django 관리 명령어

## 📋 배포 순서

### Step 1: 코드 커밋 및 푸시
```bash
cd /home/winnmedia/VideoPlanet/vridge_back

# 변경사항 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "fix: Implement robust CORS solution for Railway deployment

- Add custom CORS middleware for Railway environment
- Fix OPTIONS request handling with OptionsHandlerMiddleware
- Update middleware ordering for proper CORS processing
- Remove EOF line from Procfile
- Add comprehensive CORS testing tools"

# 푸시
git push origin main
```

### Step 2: Railway 배포 모니터링
1. Railway Dashboard에서 자동 배포 시작 확인
2. Build logs 모니터링
3. Deploy logs 확인
4. Health check 통과 확인

### Step 3: 배포 후 테스트
```bash
# 1. 헬스체크 확인
curl https://videoplanet.up.railway.app/api/health/

# 2. CORS OPTIONS 테스트
curl -X OPTIONS https://videoplanet.up.railway.app/api/health/ \
     -H "Origin: https://vlanet.net" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: content-type" -v

# 3. 실제 API 테스트
curl -X POST https://videoplanet.up.railway.app/api/auth/check-email/ \
     -H "Origin: https://vlanet.net" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com"}' -v
```

## 🔍 트러블슈팅

### 502 Bad Gateway 에러
1. Railway logs 확인: `railway logs`
2. Python 버전 확인 (3.8+ 필요)
3. 필수 패키지 설치 확인
4. 데이터베이스 연결 확인

### CORS 에러가 계속 발생하는 경우
1. 미들웨어 순서 확인 (OptionsHandlerMiddleware가 최상단)
2. Origin 허용 목록 확인
3. 브라우저 캐시 클리어
4. Railway 재시작: `railway restart`

### 데이터베이스 마이그레이션 실패
```bash
# Railway CLI로 수동 마이그레이션
railway run python manage.py migrate --settings=config.settings.railway
```

## 📝 중요 파일 목록

### 수정된 파일
- `/config/settings_base.py` - 미들웨어 설정
- `/config/settings/railway.py` - Railway 환경 설정
- `/Procfile` - 시작 명령어

### 새로 생성된 파일
- `/config/cors_solution.py` - 새 CORS 미들웨어
- `/test_cors.py` - CORS 테스트 스크립트
- `/cors_test.html` - 브라우저 테스트 페이지
- `/core/management/commands/check_cors.py` - Django 명령어
- `/CORS_FIX_GUIDE.md` - CORS 수정 가이드
- `/DEPLOYMENT_CHECKLIST.md` - 이 체크리스트

## 🎯 최종 확인 사항

- [ ] Railway 서버가 정상적으로 실행 중
- [ ] /api/health/ 엔드포인트 응답 확인
- [ ] OPTIONS 요청에 CORS 헤더 포함 확인
- [ ] vlanet.net에서 API 호출 성공
- [ ] 로그인 기능 정상 작동
- [ ] 회원가입 기능 정상 작동

## 📞 지원 필요 시

Railway 로그와 함께 다음 정보 제공:
1. `railway logs --tail 100` 출력
2. `python manage.py check_cors` 결과
3. 브라우저 개발자 도구 Network 탭 스크린샷
4. 구체적인 에러 메시지