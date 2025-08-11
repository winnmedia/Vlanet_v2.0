# VideoPlanet Development Environment Scripts

## Overview
이 디렉토리는 VideoPlanet 프로젝트의 로컬 개발 환경을 자동화하는 스크립트들을 포함합니다.

## 스크립트 목록

### 1. dev-server-start.sh
개발 서버를 시작하는 메인 스크립트입니다.

**사용법:**
```bash
# 모든 서비스 시작 (기본)
./scripts/dev-server-start.sh

# 백엔드만 시작
./scripts/dev-server-start.sh backend

# 프론트엔드만 시작
./scripts/dev-server-start.sh frontend

# 데이터베이스 서비스만 시작
./scripts/dev-server-start.sh services
```

**기능:**
- PostgreSQL 및 Redis 자동 시작 (설치된 경우)
- Django 마이그레이션 자동 실행
- Static 파일 자동 수집
- 포트 충돌 자동 해결
- 백그라운드 실행 및 로그 기록

### 2. dev-server-stop.sh
실행 중인 개발 서버를 정지합니다.

**사용법:**
```bash
# 모든 서비스 정지 (기본)
./scripts/dev-server-stop.sh

# 백엔드만 정지
./scripts/dev-server-stop.sh backend

# 프론트엔드만 정지
./scripts/dev-server-stop.sh frontend

# 전체 정지 및 로그 정리
./scripts/dev-server-stop.sh clean
```

### 3. dev-server-status.sh
개발 환경의 상태를 모니터링합니다.

**사용법:**
```bash
# 전체 상태 확인 (기본)
./scripts/dev-server-status.sh

# 간략한 상태 확인
./scripts/dev-server-status.sh brief

# 실시간 모니터링 (5초마다 갱신)
./scripts/dev-server-status.sh monitor

# JSON 포맷 출력 (CI/CD 연동용)
./scripts/dev-server-status.sh json
```

**표시 정보:**
- 서버 실행 상태 (PID, CPU, 메모리)
- 데이터베이스 연결 상태
- API 엔드포인트 헬스체크
- 시스템 리소스 사용량
- 최근 로그 활동

### 4. run-tests.sh
자동화된 테스트 실행 및 리포팅 스크립트입니다.

**사용법:**
```bash
# 모든 테스트 실행 (기본)
./scripts/run-tests.sh

# 백엔드 테스트만
./scripts/run-tests.sh backend

# 프론트엔드 테스트만
./scripts/run-tests.sh frontend

# 린팅 검사만
./scripts/run-tests.sh lint

# 보안 검사만
./scripts/run-tests.sh security

# 통합 테스트만
./scripts/run-tests.sh integration
```

**테스트 리포트:**
- 위치: `/home/winnmedia/VideoPlanet/test-reports/`
- 포맷: 로그 파일 및 JSON 요약
- 메트릭: 성공/실패/스킵 카운트, 통과율

## 디렉토리 구조

```
VideoPlanet/
├── scripts/
│   ├── dev-server-start.sh    # 서버 시작
│   ├── dev-server-stop.sh     # 서버 정지
│   ├── dev-server-status.sh   # 상태 모니터링
│   ├── run-tests.sh           # 테스트 실행
│   └── README.md             # 이 문서
├── logs/                      # 서버 로그 디렉토리
│   ├── django_server.log     # Django 서버 로그
│   ├── nextjs_server.log     # Next.js 서버 로그
│   ├── django.pid            # Django 프로세스 ID
│   └── nextjs.pid            # Next.js 프로세스 ID
└── test-reports/             # 테스트 리포트 디렉토리
    ├── django_test_*.log     # Django 테스트 결과
    ├── nextjs_test_*.log     # Next.js 테스트 결과
    ├── lint_*.log            # 린팅 결과
    ├── security_*.log        # 보안 검사 결과
    └── summary_*.json        # 테스트 요약 (JSON)
```

## 환경 요구사항

### 필수 요구사항
- Ubuntu/Debian Linux (WSL2 지원)
- Python 3.8+
- Node.js 16+
- npm 또는 yarn

### 선택적 요구사항
- PostgreSQL 12+ (없으면 Railway DB 사용)
- Redis 6+ (없으면 캐싱 기능 제한)
- Docker & Docker Compose (컨테이너 환경용)

## 포트 사용

| 서비스 | 포트 | 용도 |
|--------|------|------|
| Django Backend | 8000 | API 서버 |
| Next.js Frontend | 3000 | 웹 애플리케이션 |
| PostgreSQL | 5432 | 데이터베이스 |
| Redis | 6379 | 캐시 서버 |
| Mailhog SMTP | 1025 | 이메일 테스트 (선택) |
| Mailhog Web | 8025 | 이메일 UI (선택) |
| Adminer | 8080 | DB 관리 도구 (선택) |

## 빠른 시작 가이드

### 1. 처음 시작하기
```bash
# 저장소 클론
git clone <repository-url>
cd VideoPlanet

# 스크립트 실행 권한 부여
chmod +x scripts/*.sh

# 전체 개발 환경 시작
./scripts/dev-server-start.sh

# 상태 확인
./scripts/dev-server-status.sh
```

### 2. 일일 개발 워크플로우
```bash
# 아침: 서버 시작
./scripts/dev-server-start.sh

# 개발 중: 상태 모니터링
./scripts/dev-server-status.sh monitor

# 테스트 실행
./scripts/run-tests.sh

# 저녁: 서버 정지
./scripts/dev-server-stop.sh
```

### 3. Docker 환경 사용 (선택)
```bash
# Docker Compose로 전체 스택 실행
docker-compose -f docker-compose.dev.yml up -d

# 특정 프로파일 포함 실행
docker-compose -f docker-compose.dev.yml --profile with-nginx up -d

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f

# 정지
docker-compose -f docker-compose.dev.yml down
```

## 문제 해결

### 포트 충돌
```bash
# 특정 포트 사용 프로세스 확인
lsof -i :8000

# 강제 정리
./scripts/dev-server-stop.sh clean
```

### 권한 문제
```bash
# 스크립트 실행 권한
chmod +x scripts/*.sh

# 로그 디렉토리 권한
chmod 755 logs/
chmod 755 test-reports/
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
pg_isready

# Redis 상태 확인
redis-cli ping

# Railway DB 사용으로 전환
export DATABASE_URL="<Railway-Database-URL>"
```

## 성능 최적화 팁

1. **개발 서버 메모리 최적화**
   - Django: `--nothreading` 옵션 사용
   - Next.js: `NODE_OPTIONS='--max-old-space-size=2048'`

2. **빠른 재시작**
   ```bash
   ./scripts/dev-server-stop.sh backend && ./scripts/dev-server-start.sh backend
   ```

3. **로그 파일 정리**
   ```bash
   # 7일 이상 된 로그 삭제
   find logs/ -name "*.log" -mtime +7 -delete
   ```

## 기여 가이드

스크립트 개선 사항이나 버그를 발견하셨다면:

1. 이슈를 생성해주세요
2. 포크 후 브랜치 생성
3. 변경사항 커밋
4. Pull Request 제출

## 라이센스

이 스크립트들은 VideoPlanet 프로젝트의 일부로 제공됩니다.

## 문의

- 담당자: Robert (DevOps/Platform Lead)
- 작성일: 2025-08-11
- 버전: 1.0.0