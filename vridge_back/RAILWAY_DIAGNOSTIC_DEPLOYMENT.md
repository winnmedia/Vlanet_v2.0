# Railway 헬스체크 진단 배포 가이드

## 문제 상황
- Railway 헬스체크가 계속 실패
- 로컬에서는 성공하나 Railway에서만 실패
- 경로 문제로 추정 (95% 확률)

## 진단 도구 구성

### 1. 진단용 서버 (railway_diagnostic.py)
**목적**: Railway 환경의 상세한 정보 수집

**주요 기능**:
- 현재 작업 디렉토리 확인
- 파일 시스템 구조 출력
- Python 경로 및 환경 변수 확인
- Import 테스트 및 에러 추적
- Django 설정 테스트
- 네트워크 바인딩 테스트

**사용 방법**:
```bash
# Procfile
web: gunicorn railway_diagnostic:application --bind 0.0.0.0:$PORT --log-level debug
```

### 2. 간단한 헬스체크 서버 (railway_simple_health.py)
**목적**: 경로 문제를 우회하는 단순 헬스체크

**특징**:
- 모든 헬스체크 관련 경로에 200 OK 응답
- 최소한의 의존성
- 강제 경로 추가로 import 문제 해결

**사용 방법**:
```bash
# Procfile
web: gunicorn railway_simple_health:application --bind 0.0.0.0:$PORT
```

### 3. 직접 실행 서버 (railway_direct_health.py)
**목적**: gunicorn 없이 순수 Python으로 실행

**특징**:
- 표준 라이브러리만 사용
- 소켓 레벨에서 직접 HTTP 처리
- 의존성 제로

**사용 방법**:
```bash
# Procfile
web: python railway_direct_health.py
```

## 배포 옵션

### 옵션 1: 진단 정보 수집 (권장)
```bash
# 1. Procfile 업데이트
echo "web: ./railway_start_diagnostic.sh" > Procfile

# 2. 커밋 및 푸시
git add .
git commit -m "Add diagnostic deployment for Railway health check"
git push

# 3. Railway 로그 확인
# Railway 대시보드에서 상세한 진단 정보 확인
```

### 옵션 2: 간단한 헬스체크
```bash
# 1. Procfile 업데이트
echo "web: ./railway_start_simple_health.sh" > Procfile

# 2. 배포
git add .
git commit -m "Simple health check for Railway"
git push
```

### 옵션 3: 직접 Python 실행
```bash
# 1. Procfile 업데이트
echo "web: python railway_direct_health.py" > Procfile

# 2. 배포
git add .
git commit -m "Direct Python health check"
git push
```

## 로컬 테스트

### 진단 서버 테스트
```bash
# 자동화된 테스트
python test_diagnostic_local.py

# 수동 테스트
PORT=8888 python railway_diagnostic.py
# 다른 터미널에서
curl http://localhost:8888/health/
```

### 간단한 헬스체크 테스트
```bash
PORT=8888 python railway_simple_health.py
curl http://localhost:8888/health/
```

### 직접 실행 테스트
```bash
PORT=8888 python railway_direct_health.py
curl http://localhost:8888/health/
```

## 문제 해결 체크리스트

### Railway 로그에서 확인할 사항

1. **Python 경로 문제**
   - `ModuleNotFoundError` 확인
   - `sys.path` 출력 확인
   - 작업 디렉토리 확인

2. **포트 바인딩**
   - `PORT` 환경 변수 설정 여부
   - 바인딩 주소 (0.0.0.0 vs 127.0.0.1)
   - 포트 충돌 여부

3. **의존성 문제**
   - `gunicorn` 설치 여부
   - Django 관련 패키지
   - PostgreSQL 드라이버

4. **파일 시스템**
   - 스크립트 파일 존재 여부
   - 실행 권한
   - 경로 구조

## 예상 원인 및 해결책

### 1. 경로 문제 (가장 가능성 높음)
**증상**: ModuleNotFoundError, ImportError
**해결**: 
- `sys.path.insert(0, os.getcwd())` 추가
- 절대 경로 사용
- PYTHONPATH 환경 변수 설정

### 2. 실행 권한
**증상**: Permission denied
**해결**: 
- `chmod +x` 명령어로 실행 권한 부여
- Python 직접 실행으로 우회

### 3. 포트 바인딩
**증상**: Address already in use, Connection refused
**해결**:
- 0.0.0.0 바인딩 사용
- PORT 환경 변수 확인

### 4. 타임아웃
**증상**: Health check timeout
**해결**:
- 응답 시간 단축
- 헬스체크 타임아웃 증가
- 더 간단한 응답 반환

## 권장 진행 순서

1. **진단 배포** (railway_diagnostic.py)
   - 환경 정보 수집
   - 문제 원인 파악

2. **간단한 헬스체크** (railway_simple_health.py)
   - 최소한의 동작 확인
   - 헬스체크 통과 확인

3. **점진적 통합**
   - Django 앱 통합
   - 실제 API 엔드포인트 추가

## 모니터링 명령어

```bash
# Railway CLI 사용 시
railway logs --tail

# 웹 대시보드
# https://railway.app 에서 서비스 선택 후 Logs 탭

# 로컬 테스트
curl -v http://localhost:8888/health/
```

## 성공 기준

✅ Railway 헬스체크 통과 (200 OK)
✅ 로그에 에러 없음
✅ `/health/` 엔드포인트 정상 응답
✅ 진단 정보 수집 완료

---

**작성일**: 2025-08-12
**작성자**: DevOps Lead (Robert)
**목적**: Railway 헬스체크 실패 진단 및 해결