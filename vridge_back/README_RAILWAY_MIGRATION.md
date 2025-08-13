# Railway 프로덕션 마이그레이션 전략 가이드

## 📋 개요

Railway 프로덕션 환경에서 Django 애플리케이션의 500 에러를 해결하고 안전한 데이터베이스 마이그레이션을 수행하기 위한 종합 가이드입니다.

## 🔍 현재 상황 분석

### 마이그레이션 상태
- **결과**: 모든 마이그레이션이 이미 적용됨
- **총 앱**: 14개 (admin_dashboard, ai_video, analytics, calendars, core, documents, feedbacks, invitations, onlines, projects, users, video_analysis, video_planning, workers)
- **마이그레이션 파일**: 모든 앱에 정상적으로 존재
- **적용 상태**: `showmigrations` 결과 모든 마이그레이션에 `[X]` 표시

### 500 에러의 실제 원인
마이그레이션이 모두 적용된 상황에서 500 에러가 발생하는 경우, 다음 원인들을 고려해야 합니다:

1. **Django 설정 문제** (ALLOWED_HOSTS, CORS, 환경 변수)
2. **애플리케이션 코드 오류** (Import 에러, 런타임 에러)
3. **정적 파일 설정 문제**
4. **데이터베이스 연결 풀 문제**
5. **메모리 부족 또는 리소스 제한**

## 🛠️ 제공된 도구들

### 1. Railway 마이그레이션 전략 (`railway_migration_strategy.py`)
```bash
# 마이그레이션 상태 확인 및 안전한 실행
python3 scripts/railway_migration_strategy.py

# 강제 마이그레이션 (모든 마이그레이션이 적용되어도 재실행)
python3 scripts/railway_migration_strategy.py --force
```

**주요 기능:**
- 데이터베이스 연결 상태 확인
- 스키마 백업 생성
- 미적용 마이그레이션 탐지
- Dry-run으로 안전성 검증
- 앱별 순차적 마이그레이션 실행
- 롤백 계획 자동 생성

### 2. 데이터베이스 헬스 모니터 (`database_health_monitor.py`)
```bash
# 데이터베이스 전반적인 헬스 체크
python3 scripts/database_health_monitor.py
```

**모니터링 항목:**
- 데이터베이스 연결성 및 응답 시간
- 연결 풀 사용률
- 쿼리 성능 분석
- 데이터베이스 크기 및 테이블 통계
- 시스템 리소스 사용률

### 3. Railway 배포 자동화 (`railway_deployment_script.py`)
```bash
# 전체 배포 프로세스 (마이그레이션 포함)
python3 scripts/railway_deployment_script.py

# 마이그레이션 제외 배포
python3 scripts/railway_deployment_script.py --skip-migration

# Dry-run 모드 (실제 변경 없이 시뮬레이션)
python3 scripts/railway_deployment_script.py --dry-run
```

**배포 단계:**
1. 선행 조건 확인 (Git 상태, 환경 변수)
2. 현재 상태 백업
3. 배포 태그 생성
4. 마이그레이션 실행 (Dry-run → 실제 실행)
5. 정적 파일 수집
6. 헬스 체크

### 4. 긴급 롤백 전략 (`emergency_rollback_strategy.py`)
```bash
# 피해 상황 평가
python3 scripts/emergency_rollback_strategy.py assess

# 긴급 백업 생성
python3 scripts/emergency_rollback_strategy.py backup

# 전체 복구 절차
python3 scripts/emergency_rollback_strategy.py recover
```

**복구 기능:**
- 시스템 피해 상황 자동 평가
- 긴급 상황 백업 생성
- 마이그레이션 자동 롤백
- 백업 데이터 복원 가이드
- 수동 복구 가이드 제공

### 5. 자동화된 백업 전략 (`automated_backup_strategy.py`)
```bash
# 즉시 백업 실행
python3 scripts/automated_backup_strategy.py backup

# 백업 데몬 시작 (스케줄링)
python3 scripts/automated_backup_strategy.py daemon

# 백업 현황 보고서
python3 scripts/automated_backup_strategy.py report

# 오래된 백업 정리
python3 scripts/automated_backup_strategy.py cleanup
```

**백업 정책 (3-2-1 규칙):**
- 일일 백업: 7일 보관
- 주간 백업: 4주 보관  
- 월간 백업: 12개월 보관
- 자동 압축 및 무결성 검증

### 6. Railway 트러블슈팅 가이드 (`railway_troubleshooting_guide.py`)
```bash
# 500 에러 종합 진단
python3 scripts/railway_troubleshooting_guide.py
```

**진단 항목:**
- Railway 환경 변수 확인
- 데이터베이스 연결 테스트
- Django 설정 검증
- 정적 파일 설정 확인
- WSGI 애플리케이션 로드 테스트
- 우선순위별 해결 방안 제시

## 🚀 권장 실행 순서

### 1단계: 현재 상황 진단
```bash
# 종합 진단 실행
python3 scripts/railway_troubleshooting_guide.py

# 데이터베이스 헬스 체크
python3 scripts/database_health_monitor.py
```

### 2단계: 백업 생성
```bash
# 긴급 백업 생성
python3 scripts/emergency_rollback_strategy.py backup

# 또는 포괄적인 백업
python3 scripts/automated_backup_strategy.py backup emergency
```

### 3단계: 문제 해결
진단 결과에 따라:

**A. 마이그레이션 문제인 경우:**
```bash
python3 scripts/railway_migration_strategy.py
```

**B. 설정 문제인 경우:**
- Django 설정 파일 검토
- 환경 변수 확인
- Railway 서비스 상태 점검

**C. 애플리케이션 코드 문제인 경우:**
- Railway 로그 확인
- 코드 오류 수정
- 재배포

### 4단계: 배포 및 검증
```bash
# 안전한 배포 실행
python3 scripts/railway_deployment_script.py

# 배포 후 헬스 체크
python3 scripts/database_health_monitor.py
```

## 🔒 안전 조치

### 다운타임 최소화
- **Dry-run 모드**: 모든 변경 사항을 시뮬레이션으로 먼저 확인
- **점진적 롤아웃**: 앱별 순차 마이그레이션
- **즉시 롤백**: 문제 발생 시 자동 롤백 계획 실행

### 데이터 보호
- **자동 백업**: 모든 작업 전 데이터베이스 및 애플리케이션 백업
- **무결성 검증**: 백업 파일 압축 해제 및 구조 검증
- **3-2-1 백업 규칙**: 3개 복사본, 2개 다른 미디어, 1개 오프사이트

### 복구 계획
- **자동 복구**: 일반적인 문제에 대한 자동화된 복구 절차
- **수동 가이드**: 복잡한 상황을 위한 상세한 수동 복구 지침
- **롤백 전략**: 각 변경 사항에 대한 명확한 롤백 절차

## 📊 모니터링 및 알림

### 성능 임계값
- **연결 풀**: 80% 경고, 95% 위험
- **쿼리 시간**: 1초 경고, 5초 위험
- **디스크 사용률**: 80% 경고, 90% 위험
- **메모리 사용률**: 80% 경고, 90% 위험

### 자동 알림
- **Critical**: 데이터베이스 연결 실패, 애플리케이션 시작 실패
- **Warning**: 성능 임계값 초과, 마이그레이션 미적용
- **Info**: 정기 백업 완료, 헬스 체크 통과

## 🛡️ 보안 고려사항

### 환경 변수 보호
- **민감 정보 마스킹**: 로그에서 비밀번호, 토큰 자동 숨김
- **최소 권한 원칙**: 필요한 최소한의 데이터베이스 권한만 사용
- **암호화 전송**: SSL/TLS 연결 강제

### 백업 보안
- **압축 백업**: 저장 공간 절약 및 전송 시간 단축
- **접근 제어**: 백업 파일에 대한 제한된 접근 권한
- **보존 정책**: 자동화된 오래된 백업 정리

## 🔧 트러블슈팅 FAQ

### Q1: "모든 마이그레이션이 적용되었는데 500 에러가 발생해요"
**A**: 마이그레이션 외의 다른 원인을 확인하세요:
```bash
python3 scripts/railway_troubleshooting_guide.py
```

### Q2: "백업 복원 후에도 문제가 지속돼요"
**A**: 단계별 복구를 시도하세요:
```bash
python3 scripts/emergency_rollback_strategy.py recover
```

### Q3: "배포 중 타임아웃이 발생해요"
**A**: 배포 스크립트의 타임아웃 설정을 확인하고 단계별로 실행하세요:
```bash
python3 scripts/railway_deployment_script.py --dry-run
```

### Q4: "데이터베이스 연결이 불안정해요"
**A**: 연결 풀 설정을 확인하고 헬스 모니터링을 실행하세요:
```bash
python3 scripts/database_health_monitor.py
```

## 📞 지원 및 문의

Railway 환경에서의 추가적인 문제나 맞춤형 지원이 필요한 경우:

1. **진단 보고서 생성**: `railway_troubleshooting_guide.py` 실행
2. **로그 수집**: Railway 대시보드에서 최근 로그 다운로드
3. **환경 정보 수집**: 환경 변수 및 설정 파일 확인
4. **단계별 실행**: 각 스크립트를 단독으로 실행하여 문제 범위 축소

---

**Victoria - Database Reliability Engineer**  
*"Automate Everything, Availability First"*