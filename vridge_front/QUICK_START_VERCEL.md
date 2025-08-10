# Vercel 배포 빠른 시작 가이드

## 즉시 사용 가능한 명령어

### 1. 배포 전 검증 (필수!)
```bash
# 기본 검증
npm run validate-vercel-config

# 빌드 포함 전체 검증
npm run validate-vercel-config --with-build

# 엄격한 검증 (타입, 린트 포함)
npm run validate-vercel-config --strict --with-build
```

### 2. 안전한 배포
```bash
# 검증 후 프로덕션 배포
npm run deploy:safe

# 미리보기 배포
npm run deploy:preview
```

### 3. 모니터링
```bash
# 배포 상태 확인
npm run monitor:deploy

# 실시간 모니터링 (5분마다)
npm run monitor:deploy:watch

# 통계 리포트
npm run monitor:deploy:report
```

### 4. 긴급 롤백
```bash
# 이전 성공 배포로 롤백
./scripts/emergency-rollback.sh

# 특정 배포로 롤백
./scripts/emergency-rollback.sh [deployment-id]

# 롤백 + 헬스체크
./scripts/emergency-rollback.sh [deployment-id] --health-check
```

## 환경 변수 설정

### 1. 로컬 개발용 (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 2. Vercel 대시보드에서 설정
1. https://vercel.com/[your-team]/[your-project]/settings/environment-variables
2. 필수 변수 추가:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SITE_URL`
   - 기타 백엔드 연결 정보

### 3. GitHub Secrets 설정 (CI/CD용)
```
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
SLACK_WEBHOOK_URL (선택)
```

## 문제 해결 체크리스트

### 배포 실패 시
1. [ ] `npm run validate-vercel-config --with-build` 실행
2. [ ] 에러 메시지 확인 및 수정
3. [ ] 로컬에서 `npm run build && npm run start` 테스트
4. [ ] vercel.json 검증
5. [ ] 환경 변수 확인

### "currentUser is not defined" 오류
```typescript
// 1. 클라이언트 컴포넌트로 변경
'use client';

// 2. 조건부 렌더링 추가
{currentUser?.name || 'Guest'}

// 3. 서버 컴포넌트에서는 props로 전달
```

### "Function Runtimes" 오류
```json
// vercel.json 수정 - 유효한 런타임만 사용
{
  "functions": {
    "app/api/**.ts": {
      "runtime": "nodejs20.x"  // 또는 nodejs18.x
    }
  }
}
```

## 일일 체크리스트

### 아침 (개발 시작 전)
- [ ] `git pull` 최신 코드 받기
- [ ] `npm run monitor:deploy:report` 밤새 배포 상태 확인
- [ ] Vercel 대시보드에서 에러 로그 확인

### 점심 (중간 점검)
- [ ] `npm run validate-vercel-config` 설정 검증
- [ ] 진행 중인 PR 빌드 상태 확인

### 저녁 (배포 전)
- [ ] `npm run deploy:safe` 안전 배포 실행
- [ ] 배포 후 주요 기능 테스트
- [ ] 모니터링 알림 확인

## 팀 협업 규칙

1. **main 브랜치 직접 푸시 금지**
   - 항상 PR을 통해 머지
   - 자동 빌드 체크 통과 필수

2. **배포 전 리뷰**
   - 2명 이상 코드 리뷰
   - 체크리스트 완료 확인

3. **장애 발생 시**
   - 즉시 롤백 (`./scripts/emergency-rollback.sh`)
   - Slack에 공유
   - 사후 분석 문서 작성

## 유용한 Vercel CLI 명령어

```bash
# 로그인
vercel login

# 프로젝트 연결
vercel link

# 로그 확인
vercel logs --follow

# 환경 변수 목록
vercel env ls

# 환경 변수 추가
vercel env add

# 도메인 관리
vercel domains ls

# 빌드 로그
vercel inspect [deployment-url]
```

## 문의 및 지원

- Vercel 상태: https://www.vercel-status.com/
- 공식 문서: https://vercel.com/docs
- 내부 문서: VERCEL_NEXTJS15_GUIDELINES.md
- 체크리스트: VERCEL_DEPLOYMENT_CHECKLIST.md

---
최종 업데이트: 2025-01-12