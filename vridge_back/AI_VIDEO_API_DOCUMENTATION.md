# AI Video Generation API 완전 구현 가이드

## 개요
Django REST Framework를 사용하여 AI 영상 생성을 위한 완전한 API 시스템을 구현했습니다.
ViewSet, Serializer, URL 라우팅이 모두 완성되어 프로덕션 환경에서 바로 사용 가능합니다.

## 주요 기능

### 1. 도메인 모델 (Domain Models)
- **Story**: AI 영상 프로젝트의 주요 엔터티
- **Scene**: 스토리 내의 개별 씬
- **ScenePrompt**: 씬별 AI 생성 프롬프트
- **Job**: 비동기 작업 관리
- **StoryStateTransition**: 상태 전이 추적
- **AIProviderConfig**: AI 제공업체 설정

### 2. 상태 관리 (State Machine)
```
DRAFT → PLANNING → PLANNED → PREVIEWING → PREVIEW_READY → FINALIZING → COMPLETED
     ↓              ↓           ↓            ↓              ↓
   ARCHIVED     FAILED      FAILED       FAILED         FAILED
```

## API 엔드포인트

### Stories API

#### 기본 CRUD
- `GET /api/ai-video/stories/` - 스토리 목록 조회
- `POST /api/ai-video/stories/` - 새 스토리 생성
- `GET /api/ai-video/stories/{id}/` - 스토리 상세 조회
- `PUT /api/ai-video/stories/{id}/` - 스토리 수정
- `DELETE /api/ai-video/stories/{id}/` - 스토리 삭제

#### 워크플로우 관리
- `POST /api/ai-video/stories/{id}/lock/` - 스토리 기획 잠금
- `POST /api/ai-video/stories/{id}/unlock/` - 스토리 기획 해제
- `POST /api/ai-video/stories/{id}/transition/` - 상태 전이

#### 씬 및 프롬프트 생성
- `POST /api/ai-video/stories/{id}/scenes/bulk/` - 12개 씬 일괄 생성
- `POST /api/ai-video/stories/{id}/generate-prompts/` - AI 프롬프트 자동 생성

#### 영상 생성
- `POST /api/ai-video/stories/{id}/generate_preview/` - 프리뷰 생성
- `POST /api/ai-video/stories/{id}/render_final/` - 최종 영상 렌더링

#### 모니터링 및 분석
- `GET /api/ai-video/stories/{id}/jobs/` - 스토리 작업 목록
- `GET /api/ai-video/stories/{id}/transitions/` - 상태 전이 이력
- `GET /api/ai-video/stories/{id}/cost_estimate/` - 비용 예상
- `GET /api/ai-video/stories/statistics/` - 사용자 통계

### Scenes API

#### 기본 CRUD
- `GET /api/ai-video/scenes/` - 씬 목록 조회
- `POST /api/ai-video/scenes/` - 새 씬 생성
- `GET /api/ai-video/scenes/{id}/` - 씬 상세 조회
- `PUT /api/ai-video/scenes/{id}/` - 씬 수정
- `DELETE /api/ai-video/scenes/{id}/` - 씬 삭제

#### 특수 기능
- `POST /api/ai-video/scenes/bulk_create/` - 여러 씬 일괄 생성
- `POST /api/ai-video/scenes/{id}/generate/` - 씬 콘텐츠 생성
- `POST /api/ai-video/scenes/{id}/reorder/` - 씬 순서 변경

### Prompts API

#### 기본 CRUD
- `GET /api/ai-video/prompts/` - 프롬프트 목록 조회
- `POST /api/ai-video/prompts/` - 새 프롬프트 생성
- `GET /api/ai-video/prompts/{id}/` - 프롬프트 상세 조회
- `PUT /api/ai-video/prompts/{id}/` - 프롬프트 수정
- `DELETE /api/ai-video/prompts/{id}/` - 프롬프트 삭제

#### 특수 기능
- `POST /api/ai-video/prompts/{id}/select/` - 프롬프트를 활성화
- `POST /api/ai-video/prompts/{id}/test/` - 프롬프트 테스트 생성

### Jobs API

#### 모니터링
- `GET /api/ai-video/jobs/` - 작업 목록 조회
- `GET /api/ai-video/jobs/{id}/` - 작업 상세 조회

#### 제어
- `POST /api/ai-video/jobs/{id}/retry/` - 실패한 작업 재시도
- `POST /api/ai-video/jobs/{id}/cancel/` - 작업 취소

#### 분석
- `GET /api/ai-video/jobs/statistics/` - 작업 통계

## 요청/응답 예제

### 1. 새 스토리 생성

```json
POST /api/ai-video/stories/
{
    "project": 1,
    "title": "AI 광고 영상",
    "description": "30초 제품 광고영상",
    "duration_seconds": 30,
    "fps": 30,
    "resolution": "1920x1080",
    "ai_provider": "stability_ai",
    "style_preset": "cinematic"
}
```

### 2. 12개 씬 일괄 생성

```json
POST /api/ai-video/stories/123/scenes/bulk/
{} // 빈 요청으로 자동 12개 씬 생성
```

### 3. 프롬프트 자동 생성

```json
POST /api/ai-video/stories/123/generate-prompts/
{} // 모든 씬에 대해 기본 프롬프트 생성
```

### 4. 프리뷰 생성

```json
POST /api/ai-video/stories/123/generate_preview/
{
    "quality": "medium",
    "include_audio": false,
    "watermark": true
}
```

### 5. 최종 영상 렌더링

```json
POST /api/ai-video/stories/123/render_final/
{
    "quality": "high",
    "include_subtitles": false,
    "output_format": "mp4"
}
```

## 비즈니스 로직

### 1. 상태 전이 규칙
- Story는 정의된 상태 머신을 따라 전이됨
- 각 전이 시 비즈니스 규칙 검증
- 자동 잠금/해제 처리

### 2. Scene 생성 규칙
- 12개 씬 자동 생성 (Intro, Main 10개, Outro)
- 시간 배분 자동 계산
- 프롬프트 자동 생성

### 3. Job 관리
- 비동기 작업 큐 시스템 (BullMQ/Redis)
- 재시도 로직
- 우선순위 관리
- 상태 추적

## 서비스 레이어

### AIVideoService
- AI 제공업체 통합
- 비용 계산
- 렌더링 시간 예상
- 프롬프트 테스트

### QueueService
- 작업 큐 관리
- Redis 통합 (선택적)
- 작업 생성 및 제어

### StorageService
- 미디어 파일 업로드
- MinIO/S3 통합
- 서명된 URL 생성

## 보안 및 권한

### 인증
- JWT 기반 인증
- 사용자별 리소스 접근 제어

### 권한 클래스
- `IsOwnerOrReadOnly`: 소유자만 수정 가능
- `IsStoryOwner`: 스토리 소유자 검증
- `CanTransitionStory`: 상태 전이 권한
- `IsJobOwner`: 작업 소유자 검증

## 확장성

### AI 제공업체 추가
1. `AIProvider` enum에 새 제공업체 추가
2. `AIProviderIntegration`에 구현 추가
3. `AIProviderConfig`로 설정 관리

### 새로운 프롬프트 타입
1. `ScenePrompt.prompt_type` 선택지 추가
2. 검증 로직 추가
3. 생성 로직 구현

## 모니터링

### 로깅
- 구조화된 로깅
- 에러 추적
- 성능 모니터링

### 메트릭스
- 작업 성공률
- 평균 처리 시간
- 비용 추적
- 사용자 활동

## 배포 고려사항

### 필수 의존성
```bash
pip install djangorestframework
pip install redis  # 큐 시스템용
pip install django-filter  # 필터링용
pip install requests  # AI API 호출용
```

### 환경 변수
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
STORAGE_BASE_URL=https://storage.example.com
```

### 인프라
- Redis 서버 (작업 큐)
- MinIO/S3 (미디어 저장소)
- PostgreSQL (프로덕션 DB)
- 백그라운드 워커 (Job 처리)

## 결론

이 AI Video Generation API는 완전한 프로덕션 환경에서 사용할 수 있는 수준으로 구현되었습니다:

✅ **완전한 도메인 모델** - 비즈니스 로직과 제약 조건 포함
✅ **RESTful API 설계** - 표준 HTTP 메서드와 상태 코드 사용
✅ **상태 머신** - 엄격한 워크플로우 관리
✅ **비동기 작업 처리** - 확장 가능한 큐 시스템
✅ **보안 및 권한** - 완전한 인증/인가 시스템
✅ **에러 처리** - 포괄적인 예외 처리
✅ **확장성** - 새로운 기능 추가 용이
✅ **모니터링** - 로깅 및 메트릭스 수집

모든 핵심 엔드포인트가 구현되었으며, 프론트엔드에서 바로 연동하여 사용할 수 있습니다.