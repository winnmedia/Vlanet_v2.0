# VideoPlanet CORS 문제 해결 가이드

## 📋 수행된 작업

### 1. 새로운 CORS 미들웨어 구현
- **파일**: `config/cors_solution.py`
- **클래스**: 
  - `OptionsHandlerMiddleware`: OPTIONS 요청을 최우선으로 처리
  - `RailwayCORSMiddleware`: Railway 환경에 최적화된 CORS 처리

### 2. 미들웨어 설정 업데이트
- **파일**: `config/settings_base.py`
- **변경사항**:
  - `OptionsHandlerMiddleware`를 최상단에 배치
  - `RailwayCORSMiddleware`로 기존 CORS 미들웨어 대체
  - 기존 `corsheaders.middleware.CorsMiddleware` 비활성화

### 3. Railway 설정 정리
- **파일**: `config/settings/railway.py`
- **변경사항**:
  - CORS 설정을 명확하게 정리
  - 허용된 origin 목록 명시
  - 디버깅 출력 오류 수정

## 🚀 배포 방법

### 1. 코드 커밋 및 푸시
```bash
git add .
git commit -m "fix: Implement robust CORS solution for Railway deployment"
git push origin main
```

### 2. Railway 자동 배포
- Railway는 자동으로 새 코드를 감지하고 재배포합니다
- 배포 상태는 Railway 대시보드에서 확인 가능

### 3. 환경 변수 확인 (Railway Dashboard)
필요한 환경 변수가 설정되어 있는지 확인:
- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG=False` (프로덕션)

## 🧪 테스트 방법

### 1. Python 스크립트 테스트
```bash
# 프로덕션 환경 테스트
python test_cors.py production

# 로컬 환경 테스트
python test_cors.py local
```

### 2. 브라우저 테스트
1. `cors_test.html` 파일을 브라우저에서 열기
2. Backend URL이 올바른지 확인
3. 각 테스트 버튼 클릭하여 CORS 확인

### 3. cURL 명령어 테스트
```bash
# OPTIONS 요청 테스트
curl -X OPTIONS https://videoplanet.up.railway.app/api/health/ \
     -H "Origin: https://vlanet.net" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: content-type" -v

# POST 요청 테스트
curl -X POST https://videoplanet.up.railway.app/api/auth/check-email/ \
     -H "Origin: https://vlanet.net" \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com"}' -v
```

### 4. Django 관리 명령어
```bash
# CORS 설정 확인
python manage.py check_cors --settings=config.settings.railway
```

## ✅ 예상 결과

성공적인 CORS 응답 헤더:
```
Access-Control-Allow-Origin: https://vlanet.net
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD
Access-Control-Allow-Headers: accept, accept-encoding, authorization, content-type, ...
Access-Control-Max-Age: 86400
```

## 🔍 문제 해결

### 여전히 CORS 에러가 발생하는 경우

1. **Railway 로그 확인**
   ```bash
   railway logs
   ```

2. **미들웨어 순서 확인**
   - `OptionsHandlerMiddleware`가 최상단에 있는지 확인
   - `RailwayCORSMiddleware`가 활성화되어 있는지 확인

3. **Origin 확인**
   - 프론트엔드에서 요청하는 Origin이 허용 목록에 있는지 확인
   - `config/cors_solution.py`의 `allowed_origins` 리스트 확인

4. **캐시 문제**
   - 브라우저 캐시 클리어
   - Railway 재배포: `railway up --detach`

## 📝 핵심 변경사항 요약

1. **근본 원인**: django-cors-headers가 Railway 환경에서 제대로 작동하지 않음
2. **해결책**: 커스텀 CORS 미들웨어 구현으로 완전한 제어권 확보
3. **장점**:
   - OPTIONS 요청 즉시 처리
   - 모든 응답에 CORS 헤더 보장
   - 디버깅 로그 포함
   - Railway 환경에 최적화

## 🎯 최종 체크리스트

- [ ] 코드 변경사항 커밋
- [ ] Railway에 푸시
- [ ] 배포 완료 확인
- [ ] 프론트엔드에서 API 호출 테스트
- [ ] 로그인 기능 테스트
- [ ] 회원가입 기능 테스트

## 📞 추가 지원

문제가 지속되면 다음 정보와 함께 보고:
1. Railway 로그 (`railway logs` 출력)
2. 브라우저 개발자 도구의 Network 탭 스크린샷
3. `python manage.py check_cors` 출력 결과