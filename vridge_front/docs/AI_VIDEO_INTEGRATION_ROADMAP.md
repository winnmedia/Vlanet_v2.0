# VideoPlanet AI 영상 생성 플랫폼 통합 로드맵

## Executive Summary

AI 영상 생성 기능을 VideoPlanet에 통합하기 위한 2주 실행 계획입니다. 제한적 마이크로서비스 아키텍처를 채택하여 기존 시스템의 안정성을 유지하면서 새로운 AI 기능을 추가합니다.

## 시스템 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Frontend (Vercel)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   기존 UI    │  │  AI Studio   │  │   실시간 상태 표시      │ │
│  │  (Projects)  │  │   (New UI)   │  │   (WebSocket/SSE)       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API Gateway (Django/Railway)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   Auth/JWT   │  │  REST API    │  │   GraphQL (Future)       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Core Services   │  │  AI Services │  │  Worker Services │
│  - Projects      │  │  - Planning  │  │  - Preview Gen   │
│  - Users         │  │  - Prompting │  │  - Final Render  │
│  - Feedback      │  │  - Status    │  │  - Upscaling     │
└──────────────────┘  └──────────────┘  └──────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
        ┌──────────────────────────────────────────┐
        │           Data Layer                      │
        │  ┌────────┐  ┌────────┐  ┌────────────┐ │
        │  │Postgres│  │ Redis  │  │  MinIO/S3  │ │
        │  └────────┘  └────────┘  └────────────┘ │
        └──────────────────────────────────────────┘
```

## Phase 1: 기반 인프라 구축 (Day 1-3)

### Day 1: Queue 시스템 및 Worker 아키텍처

#### 1.1 Redis 설정 (Railway)
```bash
# Railway CLI 또는 대시보드에서
railway add redis
railway link

# 환경변수 설정
REDIS_URL=redis://:password@host:port
```

#### 1.2 BullMQ Queue 구현
```javascript
// /worker-service/src/queues/videoQueue.js
import { Queue, Worker, QueueScheduler } from 'bullmq';
import Redis from 'ioredis';

const connection = new Redis(process.env.REDIS_URL);

export const videoQueue = new Queue('video-generation', {
  connection,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
    removeOnComplete: false,
    removeOnFail: false,
  },
});

// Scheduler for delayed jobs
new QueueScheduler('video-generation', { connection });
```

#### 1.3 Worker Pool 구현
```javascript
// /worker-service/src/workers/previewWorker.js
export class PreviewWorker {
  constructor() {
    this.worker = new Worker(
      'video-generation',
      async (job) => {
        const { type, data } = job.data;
        
        switch (type) {
          case 'preview':
            return await this.generatePreview(data);
          case 'final':
            return await this.generateFinal(data);
          default:
            throw new Error(`Unknown job type: ${type}`);
        }
      },
      {
        connection,
        concurrency: 5, // 동시 처리 작업 수
      }
    );
  }
  
  async generatePreview(data) {
    // 구현 예정
    await job.updateProgress(10);
    // ... AI 처리 로직
    await job.updateProgress(100);
  }
}
```

### Day 2: Storage 및 State Machine

#### 2.1 MinIO/S3 설정
```javascript
// /worker-service/src/services/storage.js
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

export class StorageService {
  constructor() {
    this.client = new S3Client({
      endpoint: process.env.MINIO_ENDPOINT,
      region: 'us-east-1',
      credentials: {
        accessKeyId: process.env.MINIO_ACCESS_KEY,
        secretAccessKey: process.env.MINIO_SECRET_KEY,
      },
      forcePathStyle: true,
    });
  }
  
  async uploadVideo(buffer, key) {
    const command = new PutObjectCommand({
      Bucket: 'videos',
      Key: key,
      Body: buffer,
      ContentType: 'video/mp4',
    });
    
    return await this.client.send(command);
  }
  
  async getPresignedUrl(key, expiresIn = 3600) {
    const command = new GetObjectCommand({
      Bucket: 'videos',
      Key: key,
    });
    
    return await getSignedUrl(this.client, command, { expiresIn });
  }
}
```

#### 2.2 State Machine 구현
```typescript
// /videoplanet-clean/src/lib/stateMachine.ts
export enum VideoState {
  DRAFT = 'draft',
  PLANNING = 'planning',
  PLANNED = 'planned',
  PREVIEWING = 'previewing',
  PREVIEW_READY = 'preview_ready',
  RENDERING = 'rendering',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export const transitions = {
  [VideoState.DRAFT]: [VideoState.PLANNING],
  [VideoState.PLANNING]: [VideoState.PLANNED, VideoState.DRAFT],
  [VideoState.PLANNED]: [VideoState.PREVIEWING, VideoState.PLANNING],
  [VideoState.PREVIEWING]: [VideoState.PREVIEW_READY, VideoState.FAILED],
  [VideoState.PREVIEW_READY]: [VideoState.RENDERING, VideoState.PLANNED],
  [VideoState.RENDERING]: [VideoState.COMPLETED, VideoState.FAILED],
  [VideoState.FAILED]: [VideoState.PLANNING, VideoState.DRAFT],
};

export function canTransition(from: VideoState, to: VideoState): boolean {
  return transitions[from]?.includes(to) ?? false;
}
```

### Day 3: Django Backend 통합

#### 3.1 Django Models
```python
# /vridge_back/ai_video/models.py
from django.db import models
from django.contrib.postgres.fields import JSONField

class AIVideoProject(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('planning', 'Planning'),
        ('planned', 'Planned'),
        ('previewing', 'Previewing'),
        ('preview_ready', 'Preview Ready'),
        ('rendering', 'Rendering'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Story and prompts
    story_title = models.CharField(max_length=200)
    story_description = models.TextField()
    character_prompt = models.TextField()
    background_prompt = models.TextField()
    action_prompt = models.TextField()
    
    # Generation parameters
    style = models.CharField(max_length=50, default='realistic')
    duration = models.IntegerField(default=6)  # seconds
    resolution = models.CharField(max_length=20, default='1080p')
    fps = models.IntegerField(default=30)
    
    # Results
    preview_url = models.URLField(null=True, blank=True)
    final_url = models.URLField(null=True, blank=True)
    thumbnail_url = models.URLField(null=True, blank=True)
    
    # Metadata
    generation_params = models.JSONField(default=dict)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_video_projects'
        ordering = ['-created_at']
```

#### 3.2 API Endpoints
```python
# /vridge_back/ai_video/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
import redis
import json

class AIVideoProjectViewSet(viewsets.ModelViewSet):
    serializer_class = AIVideoProjectSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def generate_preview(self, request, pk=None):
        video_project = self.get_object()
        
        # Validate state transition
        if video_project.status != 'planned':
            return Response(
                {'error': 'Video must be in planned state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Update status
            video_project.status = 'previewing'
            video_project.save()
            
            # Create job
            job = GenerationJob.objects.create(
                video_project=video_project,
                job_type='preview',
                status='queued'
            )
            
            # Add to queue
            redis_client = redis.from_url(settings.REDIS_URL)
            job_data = {
                'id': str(job.id),
                'type': 'preview',
                'video_project_id': video_project.id,
                'prompts': {
                    'character': video_project.character_prompt,
                    'background': video_project.background_prompt,
                    'action': video_project.action_prompt,
                },
                'params': video_project.generation_params,
            }
            
            redis_client.lpush('bull:video-generation:wait', json.dumps(job_data))
        
        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'video_{video_project.id}',
            {
                'type': 'status_update',
                'message': {
                    'status': 'previewing',
                    'job_id': str(job.id),
                }
            }
        )
        
        return Response({
            'job_id': str(job.id),
            'status': 'queued',
            'estimated_time': 30,  # seconds
        })
```

## Phase 2: AI Integration (Day 4-7)

### Day 4-5: AI Provider 추상화

#### 4.1 Provider Interface
```typescript
// /worker-service/src/providers/types.ts
export interface AIProvider {
  name: string;
  generateImage(prompt: string, params?: ImageParams): Promise<Buffer>;
  generateVideo(images: Buffer[], params?: VideoParams): Promise<Buffer>;
  upscale(video: Buffer, targetResolution: Resolution): Promise<Buffer>;
  estimateCost(params: GenerationParams): number;
}

export interface ImageParams {
  width: number;
  height: number;
  style: string;
  seed?: number;
  steps?: number;
}

export interface VideoParams {
  duration: number;
  fps: number;
  motion: 'slow' | 'medium' | 'fast';
}
```

#### 4.2 Stability AI Provider
```typescript
// /worker-service/src/providers/stability.ts
import axios from 'axios';

export class StabilityAIProvider implements AIProvider {
  private apiKey: string;
  private baseUrl = 'https://api.stability.ai/v1';
  
  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }
  
  async generateImage(prompt: string, params?: ImageParams): Promise<Buffer> {
    const response = await axios.post(
      `${this.baseUrl}/generation/stable-diffusion-xl-1024-v1-0/text-to-image`,
      {
        text_prompts: [{ text: prompt, weight: 1 }],
        cfg_scale: 7,
        height: params?.height || 1024,
        width: params?.width || 1024,
        steps: params?.steps || 30,
        samples: 1,
      },
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        responseType: 'arraybuffer',
      }
    );
    
    return Buffer.from(response.data);
  }
  
  estimateCost(params: GenerationParams): number {
    // $0.002 per image
    return 0.002 * (params.images || 1);
  }
}
```

### Day 6-7: 영상 처리 파이프라인

#### 6.1 Composite Service
```javascript
// /worker-service/src/services/composite.js
import sharp from 'sharp';
import ffmpeg from 'fluent-ffmpeg';

export class CompositeService {
  async separateLayers(image) {
    // AI 기반 인물/배경 분리
    const { foreground, background } = await this.runSegmentation(image);
    
    return {
      character: await sharp(foreground).png().toBuffer(),
      background: await sharp(background).png().toBuffer(),
    };
  }
  
  async mergeLayersToVideo(layers, duration = 6) {
    return new Promise((resolve, reject) => {
      const command = ffmpeg();
      
      // 각 레이어를 입력으로 추가
      layers.forEach((layer, index) => {
        command.input(layer);
      });
      
      command
        .complexFilter([
          // 배경 위에 캐릭터 오버레이
          '[0][1]overlay=x=(W-w)/2:y=(H-h)/2',
          // 모션 효과 추가
          'zoompan=z=1.1:d=25:s=1920x1080',
        ])
        .outputOptions([
          '-c:v libx264',
          '-preset fast',
          '-crf 22',
          '-pix_fmt yuv420p',
          `-t ${duration}`,
        ])
        .on('end', () => resolve())
        .on('error', reject)
        .save('output.mp4');
    });
  }
}
```

#### 6.2 Upscale Service
```javascript
// /worker-service/src/services/upscale.js
export class UpscaleService {
  async upscaleVideo(inputBuffer, targetResolution = '1080p') {
    // Real-ESRGAN 또는 Topaz 통합
    const upscaled = await this.runESRGAN(inputBuffer, {
      scale: 2,
      model: 'realesrgan-x4plus',
    });
    
    // Frame interpolation for smooth motion
    const interpolated = await this.runRIFE(upscaled, {
      targetFps: 60,
      model: 'rife-v4.6',
    });
    
    // Final encoding
    return await this.encode(interpolated, targetResolution);
  }
}
```

## Phase 3: Frontend UI 구현 (Day 8-10)

### Day 8: AI Studio UI

#### 8.1 Story Planning Interface
```tsx
// /videoplanet-clean/src/components/ai-studio/StoryPlanner.tsx
import { useState } from 'react';
import { useAIVideoProject } from '@/hooks/useAIVideoProject';

export function StoryPlanner({ projectId }: { projectId: string }) {
  const { project, updateProject } = useAIVideoProject(projectId);
  const [activeStep, setActiveStep] = useState(0);
  
  const steps = [
    { id: 'story', label: '스토리 작성', component: StoryEditor },
    { id: 'character', label: '인물 설정', component: CharacterDesigner },
    { id: 'background', label: '배경 설정', component: BackgroundDesigner },
    { id: 'action', label: '액션 정의', component: ActionDefiner },
    { id: 'preview', label: '미리보기', component: PreviewGenerator },
  ];
  
  return (
    <div className="flex h-screen">
      {/* Sidebar with steps */}
      <div className="w-64 bg-gray-50 border-r">
        <StepIndicator steps={steps} activeStep={activeStep} />
      </div>
      
      {/* Main content area */}
      <div className="flex-1 p-8">
        {React.createElement(steps[activeStep].component, {
          project,
          onUpdate: updateProject,
          onNext: () => setActiveStep(prev => prev + 1),
        })}
      </div>
      
      {/* Right panel with AI suggestions */}
      <div className="w-96 bg-gray-50 border-l p-6">
        <AISuggestions 
          context={project} 
          currentStep={steps[activeStep].id}
        />
      </div>
    </div>
  );
}
```

#### 8.2 Real-time Status Updates
```tsx
// /videoplanet-clean/src/components/ai-studio/GenerationStatus.tsx
import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

export function GenerationStatus({ jobId }: { jobId: string }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('queued');
  const [logs, setLogs] = useState<string[]>([]);
  
  const { subscribe } = useWebSocket();
  
  useEffect(() => {
    const unsubscribe = subscribe(`job.${jobId}`, (event) => {
      switch (event.type) {
        case 'progress':
          setProgress(event.data.percent);
          break;
        case 'status':
          setStatus(event.data.status);
          break;
        case 'log':
          setLogs(prev => [...prev, event.data.message]);
          break;
      }
    });
    
    return unsubscribe;
  }, [jobId]);
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">생성 진행률</span>
        <span className="text-sm text-gray-500">{progress}%</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-xs">
        {logs.map((log, i) => (
          <div key={i}>{log}</div>
        ))}
      </div>
    </div>
  );
}
```

### Day 9-10: 통합 테스트 및 최적화

#### 9.1 E2E Test Suite
```typescript
// /videoplanet-clean/tests/e2e/ai-video-generation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('AI Video Generation Flow', () => {
  test('complete generation workflow', async ({ page }) => {
    // 1. Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // 2. Create AI Video Project
    await page.goto('/projects/123/ai-studio');
    
    // 3. Fill story details
    await page.fill('[name="story_title"]', 'Test Video');
    await page.fill('[name="story_description"]', 'A test video description');
    await page.click('button:has-text("다음")');
    
    // 4. Set character prompt
    await page.fill('[name="character_prompt"]', 'A hero character');
    await page.click('button:has-text("다음")');
    
    // 5. Set background
    await page.fill('[name="background_prompt"]', 'Fantasy landscape');
    await page.click('button:has-text("다음")');
    
    // 6. Generate preview
    await page.click('button:has-text("미리보기 생성")');
    
    // 7. Wait for preview
    await expect(page.locator('.preview-video')).toBeVisible({ timeout: 60000 });
    
    // 8. Generate final
    await page.click('button:has-text("최종본 생성")');
    
    // 9. Verify completion
    await expect(page.locator('.final-video')).toBeVisible({ timeout: 300000 });
  });
});
```

## 성능 최적화 전략

### 캐싱 전략
```javascript
// Redis 기반 다층 캐싱
const cacheStrategy = {
  L1: {
    // 메모리 캐시 (Worker 내부)
    storage: 'memory',
    ttl: 60, // 1분
    size: '100MB',
  },
  L2: {
    // Redis 캐시
    storage: 'redis',
    ttl: 3600, // 1시간
    patterns: ['prompts', 'thumbnails'],
  },
  L3: {
    // CDN/S3 캐시
    storage: 's3',
    ttl: 86400, // 24시간
    patterns: ['videos', 'images'],
  },
};
```

### 병렬 처리 최적화
```javascript
// 병렬 처리 파이프라인
async function optimizedPipeline(job) {
  // 병렬로 처리 가능한 작업들
  const [character, background, audio] = await Promise.all([
    generateCharacter(job.character_prompt),
    generateBackground(job.background_prompt),
    generateAudio(job.audio_prompt),
  ]);
  
  // 순차 처리 필요한 작업
  const composite = await mergeElements(character, background);
  const animated = await addMotion(composite, job.motion_params);
  const withAudio = await addAudioTrack(animated, audio);
  
  return await finalRender(withAudio);
}
```

## 모니터링 및 알림

### Prometheus 메트릭
```yaml
# /monitoring/prometheus-metrics.yml
metrics:
  - name: video_generation_duration
    type: histogram
    help: Time taken to generate video
    labels: [type, status]
    
  - name: ai_api_calls_total
    type: counter
    help: Total number of AI API calls
    labels: [provider, endpoint]
    
  - name: generation_cost_dollars
    type: gauge
    help: Cost of video generation
    labels: [project_id]
    
  - name: queue_depth
    type: gauge
    help: Number of jobs in queue
    labels: [queue_name, status]
```

### 알림 규칙
```yaml
# /monitoring/alerts.yml
alerts:
  - name: HighFailureRate
    expr: rate(video_generation_failures[5m]) > 0.1
    severity: critical
    action: page_oncall
    
  - name: LongQueueTime
    expr: avg(queue_wait_time) > 120
    severity: warning
    action: notify_slack
    
  - name: HighCost
    expr: sum(generation_cost_dollars) > 1000
    severity: info
    action: email_finance
```

## 배포 체크리스트

### Pre-deployment
- [ ] 환경변수 설정 완료
- [ ] Redis 인스턴스 준비
- [ ] S3/MinIO 버킷 생성
- [ ] AI API 키 확보
- [ ] SSL 인증서 준비

### Deployment
- [ ] Database 마이그레이션 실행
- [ ] Worker 서비스 배포
- [ ] Frontend 빌드 및 배포
- [ ] Health check 확인
- [ ] Smoke test 실행

### Post-deployment
- [ ] 모니터링 대시보드 확인
- [ ] 성능 메트릭 검증
- [ ] 사용자 피드백 수집
- [ ] 비용 추적 시작
- [ ] 문서 업데이트

## 팀 역할 분담

| 담당자 | 역할 | 책임 영역 |
|--------|------|----------|
| Arthur | Chief Architect | 전체 아키텍처, 기술 결정 |
| Benjamin | Backend Lead | Django API, 데이터 모델 |
| Sophia | Frontend Lead | UI/UX, React 컴포넌트 |
| Noah | API Developer | Worker 서비스, AI 통합 |
| Chloe | Integration Engineer | 시스템 통합, 배포 |
| Emily | DevOps | CI/CD, 모니터링 |
| Henry | QA Engineer | 테스트 자동화 |

## 리스크 관리

### 기술적 리스크
1. **AI API 제한**: Rate limiting 대응, 폴백 provider 준비
2. **비용 초과**: 실시간 비용 모니터링, 자동 차단 임계값
3. **성능 저하**: 오토스케일링, 캐싱 전략

### 비즈니스 리스크
1. **품질 이슈**: A/B 테스트, 사용자 피드백 루프
2. **경쟁사 대응**: 차별화 기능 지속 개발
3. **규제 준수**: 저작권 필터링, 이용약관 업데이트

## 성공 지표 (KPI)

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 생성 성공률 | > 95% | successful_jobs / total_jobs |
| 평균 생성 시간 | < 60초 | avg(completion_time) |
| 사용자 만족도 | > 4.0/5 | NPS 설문 |
| 비용 효율성 | < $2/video | total_cost / videos_generated |
| 시스템 가용성 | > 99.9% | uptime / total_time |

---

**작성일**: 2025-01-09  
**다음 검토**: 2025-01-16  
**버전**: 1.0.0