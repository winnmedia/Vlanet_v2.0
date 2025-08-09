# 📊 VideoPlanet 핵심 기능 목록 및 우선순위

## 🎯 Week 1: 기반 구축

### Day 1-3: P0 - 필수 기반 기능

#### 1. 🔐 인증 시스템
- **JWT 기반 인증**
  - [x] 로그인/로그아웃
  - [x] 회원가입
  - [x] 토큰 자동 갱신 (Refresh Token)
  - [x] 401 에러 시 자동 재시도
- **소셜 로그인**
  - [x] Google OAuth 2.0
  - [x] Kakao OAuth 2.0
- **계정 관리**
  - [x] 이메일 인증
  - [x] 비밀번호 재설정
  - [x] 비밀번호 변경
- **권한 관리**
  - [x] Admin (관리자)
  - [x] Manager (매니저)
  - [x] Creator (제작자)
  - [x] Viewer (뷰어)

#### 2. 📁 프로젝트 관리 기본
- **CRUD 작업**
  - [x] 프로젝트 생성
  - [x] 프로젝트 목록 조회
  - [x] 프로젝트 상세 조회
  - [x] 프로젝트 수정
  - [x] 프로젝트 삭제
- **팀 협업**
  - [x] 팀원 초대
  - [x] 역할 지정 (Owner/Manager/Member/Viewer)
  - [x] 권한 관리
  - [x] 팀원 제거
- **프로젝트 관리**
  - [x] 상태 관리 (기획→제작→검토→완료)
  - [x] 파일 업로드 (최대 100MB)
  - [x] 썸네일 설정
  - [x] 태그 관리
- **검색 및 필터**
  - [x] 키워드 검색
  - [x] 상태별 필터링
  - [x] 날짜 범위 필터
  - [x] 페이지네이션

### Day 4-7: P1 - 핵심 비즈니스 기능

#### 3. 🎬 영상 기획 시스템
- **스토리 개발**
  - [x] 스토리 작성/편집
  - [x] 다중 스토리 버전 관리
  - [x] 스토리 전개 방식 선택(프레임워크)
  - [x] 스토리 내용 입력 및 주인공 설정
- **씬(Scene) 관리**
  - [x] 씬 생성/수정/삭제
  - [x] 씬 순서 변경 (드래그 앤 드롭)
  - [x] 씬 복제
  - [x] 씬별 설정 (장소, 시간, 분위기)
- **숏(Shot) 설정**
  - [x] 숏 리스트 생성
  - [x] 카메라 앵글 설정
  - [x] 카메라 무브먼트 정의
  - [x] 숏 길이 설정
- **콘티(Storyboard)**
  - [x] 콘티 프레임 생성
  - [x] 이미지 업로드/그리기
  - [x] 프레임별 설명 추가
  - [x] 콘티 순서 조정
- **AI 기능**
  - [x] DALL-E 3 프롬프트 자동 생성
  - [x] Midjourney 프롬프트 최적화
  - [x] VEO3 비디오 프롬프트 생성
  - [x] GPT-4 기반 스토리 제안
- **내보내기**
  - [x] PDF 기획안 생성
  - [x] PPT 프레젠테이션 내보내기
  - [x] 템플릿 저장
  - [x] 템플릿 불러오기

## 🚀 Week 2: 협업 및 고도화

### Day 8-10: P2 - 협업 기능

#### 4. 💬 피드백 시스템
- **비디오 플레이어**
  - [x] HLS 스트리밍 지원
  - [x] 다중 해상도 (360p/720p/1080p)
  - [x] 재생 속도 조절
  - [x] 구간 반복
  - [x] 스크린샷 캡처
- **타임라인 피드백**
  - [x] 타임코드 기반 코멘트
  - [x] 프레임별 주석
  - [x] 드로잉 툴
  - [x] 코멘트 스레드
  - [x] 피드백 및 코멘트에 댓글 생성 및 관리
  - [x] 피드백 및 코멘트에 감정 표현(좋아요, 싫어요, 애매해요)
- **협업 기능**
  - [x] 실시간 동기화 (WebSocket)
  - [x] @멘션 기능
  - [x] 피드백 상태 (Open/In Progress/Resolved/Closed)
  - [x] 우선순위 설정
- **알림**
  - [x] 브라우저 푸시 알림
  - [x] 이메일 알림
  - [x] 인앱 알림
  - [x] 알림 설정 커스터마이징
- **버전 관리**
  - [x] 버전 히스토리
  - [x] 버전 비교
  - [x] 변경사항 추적
- **외부 공유**
  - [x] 게스트 초대 링크
  - [x] 비밀번호 보호
  - [x] 만료 기간 설정
  - [x] 권한 제한

### Day 11-13: P3 - 프로젝트 관리 고도화

#### 5. 📅 캘린더 & 일정 관리
- **캘린더 뷰**
  - [x] 월별 보기
  - [x] 주별 보기
  - [x] 일별 보기
  - [x] 연간 보기
- **간트차트**
  - [x] 프로젝트 타임라인
  - [x] 의존성 관계 표시
  - [x] 진행률 표시
  - [x] 크리티컬 패스
- **일정 관리**
  - [x] 일정 생성/수정/삭제
  - [x] 반복 일정
  - [x] 일정 충돌 감지
  - [x] 자동 일정 조정
- **마일스톤**
  - [x] 마일스톤 설정
  - [x] 진행 상황 추적
  - [x] 지연 알림
- **통합**
  - [x] Google Calendar 연동 (준비)
  - [x] Outlook Calendar 연동 (준비)
  - [x] iCal 내보내기
- **리마인더**
  - [x] 자동 리마인더
  - [x] 커스텀 알림
  - [x] 이메일/SMS 알림

### Day 14: P4 - 사용자 경험

#### 6. 👤 마이페이지 & 대시보드
- **프로필 관리**
  - [x] 기본 정보 수정
  - [x] 프로필 이미지 업로드
  - [x] 자기소개 작성
  - [x] 연락처 정보
- **활동 내역**
  - [x] 프로젝트 참여 히스토리
  - [x] 피드백 활동 로그
  - [x] 작업 통계
  - [x] 기여도 분석
- **대시보드**
  - [x] 진행중 프로젝트 위젯
  - [x] 최근 피드백 위젯
  - [x] 다가오는 일정 위젯
  - [x] 팀 활동 피드
  - [x] 위젯 커스터마이징
- **알림 설정**
  - [x] 알림 유형별 on/off
  - [x] 알림 시간대 설정
  - [x] 알림 채널 선택
- **개인 설정**
  - [x] 언어 설정
  - [x] 테마 설정 (라이트/다크)
  - [x] 타임존 설정
  - [x] 접근성 옵션

## 📋 기술 구현 명세

### Frontend 기술 스택
```javascript
{
  "framework": "Next.js 15.1",
  "language": "TypeScript 5.x",
  "styling": "Tailwind CSS 3.4",
  "state": "Zustand 5.x",
  "api": "TanStack Query 5.x",
  "forms": "React Hook Form + Zod",
  "testing": "Vitest + Playwright"
}
```

### Backend API 엔드포인트
```typescript
const API_BASE = 'https://videoplanet.up.railway.app/api';

const endpoints = {
  auth: {
    login: '/auth/login/',
    signup: '/auth/signup/',
    refresh: '/auth/refresh/',
    me: '/auth/me/',
    verify: '/auth/verify/',
    reset: '/auth/password-reset/'
  },
  projects: {
    list: '/projects/',
    create: '/projects/create/',
    detail: '/projects/detail/{id}/',
    update: '/projects/update/{id}/',
    delete: '/projects/delete/{id}/',
    invite: '/projects/invite/{id}/',
    members: '/projects/{id}/members/'
  },
  planning: {
    list: '/video-planning/',
    create: '/video-planning/create/',
    detail: '/video-planning/detail/{id}/',
    generateStory: '/video-planning/generate/story/',
    generateScenes: '/video-planning/generate/scenes/',
    generateShots: '/video-planning/generate/shots/',
    generateStoryboards: '/video-planning/generate/storyboards/',
    aiPrompt: '/video-planning/ai/generate-prompt/',
    veo3Prompt: '/video-planning/ai/generate-veo3-prompt/',
    exportPdf: '/video-planning/export/pdf/'
  },
  feedback: {
    list: '/feedbacks/',
    create: '/feedbacks/create/',
    detail: '/feedbacks/{id}/',
    comments: '/feedbacks/{id}/comments/',
    upload: '/feedbacks/upload/',
    stream: '/feedbacks/{id}/stream/'
  },
  calendar: {
    events: '/calendar/events/',
    create: '/calendar/events/create/',
    update: '/calendar/events/{id}/',
    delete: '/calendar/events/{id}/',
    milestones: '/calendar/milestones/'
  },
  users: {
    profile: '/users/profile/',
    update: '/users/profile/update/',
    uploadImage: '/users/profile/upload-image/',
    notifications: '/users/notifications/',
    settings: '/users/settings/'
  }
};
```

## ✅ 품질 기준 및 성공 지표

### 성능 목표
| 지표 | 목표값 | 측정 방법 |
|------|--------|-----------|
| LCP (Largest Contentful Paint) | < 2.5초 | Lighthouse |
| FID (First Input Delay) | < 100ms | Lighthouse |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| TTI (Time to Interactive) | < 3.5초 | Lighthouse |
| API 응답 시간 | < 500ms | 네트워크 모니터링 |
| 빌드 시간 | < 2분 | CI/CD |
| 번들 크기 (초기 JS) | < 200KB | Webpack Analyzer |

### 테스트 커버리지
| 우선순위 | 기능 | 목표 커버리지 | 테스트 유형 |
|---------|------|--------------|-------------|
| P0 | 인증 시스템 | 95% | Unit + Integration + E2E |
| P0 | 프로젝트 CRUD | 95% | Unit + Integration + E2E |
| P1 | 영상 기획 | 85% | Unit + Integration |
| P2 | 피드백 시스템 | 80% | Unit + Integration |
| P3 | 캘린더 | 75% | Unit + Integration |
| P4 | 마이페이지 | 70% | Unit |

### 브라우저 호환성
- ✅ Chrome 90+ (데스크톱/모바일)
- ✅ Safari 14+ (데스크톱/모바일)
- ✅ Edge 90+
- ✅ Firefox 88+

### 반응형 디자인
- ✅ 모바일 (320px - 768px)
- ✅ 태블릿 (768px - 1024px)
- ✅ 데스크톱 (1024px - 1920px)
- ✅ 대형 모니터 (1920px+)

## 📅 2주 개발 일정표

### Week 1 체크포인트
| Day | 날짜 | 목표 | 검증 방법 | 완료 |
|-----|------|------|----------|------|
| 1 | 08/09 | 프로젝트 셋업 + 인증 UI | 로그인/회원가입 화면 | ⬜ |
| 2 | 08/10 | 인증 API 연동 | JWT 토큰 발급/갱신 | ⬜ |
| 3 | 08/11 | 프로젝트 CRUD | 프로젝트 생성/수정 | ⬜ |
| 4 | 08/12 | 영상 기획 UI (스토리) | 스토리 편집 가능 | ⬜ |
| 5 | 08/13 | 영상 기획 UI (씬/숏) | 씬/숏 관리 가능 | ⬜ |
| 6 | 08/14 | AI 프롬프트 연동 | DALL-E 프롬프트 생성 | ⬜ |
| 7 | 08/15 | PDF 내보내기 | 기획안 PDF 다운로드 | ⬜ |

### Week 2 체크포인트
| Day | 날짜 | 목표 | 검증 방법 | 완료 |
|-----|------|------|----------|------|
| 8 | 08/16 | 피드백 비디오 플레이어 | 비디오 재생 | ⬜ |
| 9 | 08/17 | 타임라인 코멘트 | 코멘트 작성/조회 | ⬜ |
| 10 | 08/18 | WebSocket 실시간 | 실시간 동기화 | ⬜ |
| 11 | 08/19 | 캘린더 뷰 | 일정 표시 | ⬜ |
| 12 | 08/20 | 간트차트 | 프로젝트 타임라인 | ⬜ |
| 13 | 08/21 | 마이페이지 | 프로필 수정 | ⬜ |
| 14 | 08/22 | 통합 테스트 + 배포 | 전체 플로우 검증 | ⬜ |

## 🚦 리스크 관리

### 주요 리스크 및 대응 방안
| 리스크 | 확률 | 영향도 | 대응 방안 |
|--------|------|--------|-----------|
| 2주 일정 지연 | 중 | 높음 | P0/P1 기능 우선 구현, P3/P4 단계적 배포 |
| API 호환성 이슈 | 낮음 | 높음 | API 문서 기반 Mock 데이터 우선 개발 |
| 성능 목표 미달 | 중 | 중간 | 점진적 최적화, 코드 스플리팅 |
| 브라우저 호환성 | 낮음 | 중간 | Polyfill 적용, 점진적 개선 |
| 테스트 커버리지 부족 | 중 | 낮음 | Critical Path 우선 테스트 |

## 📝 참고 사항

### 개발 원칙
1. **MVP First**: 핵심 기능 우선 구현 후 점진적 개선
2. **API First**: Backend API 스펙 기반 개발
3. **Mobile First**: 모바일 우선 반응형 디자인
4. **Test Driven**: 핵심 로직 TDD 적용
5. **Clean Code**: 일관된 코드 스타일, 명확한 네이밍

### 커뮤니케이션
- 일일 진행 상황 체크
- 블로커 발생 시 즉시 보고
- 주요 마일스톤 완료 시 데모

### 문서화
- API 연동 가이드
- 컴포넌트 사용 가이드
- 배포 가이드
- 트러블슈팅 가이드

---

*최종 업데이트: 2025-08-08*
*작성자: VideoPlanet Development Team*