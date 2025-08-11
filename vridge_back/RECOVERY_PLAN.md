# 📋 VideoPlanet 복구 계획

## 현재 상태 ✅
- 헬스체크: **작동 중** (server_simple.py)
- Django: **미작동**
- 로그인: **미작동**
- 데이터베이스: **확인 필요**

## 단계별 복구 계획

### 1단계: 현재 상태 유지 (완료) ✅
```
server_simple.py로 헬스체크만 유지
```

### 2단계: 하이브리드 서버 테스트
```bash
# Railway 대시보드에서:
Start Command: python hybrid_server.py
```

이 서버는:
- 헬스체크는 항상 작동
- Django가 준비되면 자동으로 API 활성화
- Django 실패해도 서버는 계속 실행

### 3단계: Django 복구
1. 데이터베이스 연결 확인
2. 마이그레이션 실행
3. 로깅 레벨 조정

### 4단계: 전체 서비스 복구
```bash
# 최종 목표:
Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --log-level ERROR
```

## 현재 작동하는 설정
```json
{
  "startCommand": "python server_simple.py",
  "healthcheckPath": "/api/health/",
  "PORT": "8000"
}
```

## 다음 시도할 명령어
1. `python hybrid_server.py` - Django 점진적 복구
2. `python minimal_server.py` - JSON 응답 헬스체크
3. `./start_emergency.sh` - 최소 Django 시작

## Railway 환경 변수 확인
```
DJANGO_SETTINGS_MODULE=config.settings.railway
DATABASE_URL=(PostgreSQL URL)
SECRET_KEY=(자동 생성된 값)
DEBUG=False
PYTHONUNBUFFERED=1
PORT=8000
```

## 문제 해결 체크리스트
- [ ] PostgreSQL 연결 가능한가?
- [ ] users_user 테이블 존재하는가?
- [ ] deletion_reason 필드 문제 해결됐는가?
- [ ] Rate limit 문제 해결됐는가?
- [ ] CORS 헤더 정상 작동하는가?

## 긴급 연락처
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app