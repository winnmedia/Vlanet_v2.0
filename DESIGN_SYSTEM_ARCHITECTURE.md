# VideoPlanet 디자인 시스템 아키텍처

## 🎨 디자인 시스템 개요

VideoPlanet의 디자인 시스템은 영상 제작 워크플로우에 특화된 일관되고 확장 가능한 UI/UX 경험을 제공합니다.

## 📐 1. 디자인 토큰 정의

### 1.1 색상 시스템 (Color System)

#### 브랜드 색상
```javascript
const colors = {
  brand: {
    primary: '#1631F8',      // 메인 블루 - 모든 주요 액션
    primaryDark: '#0F23C9',  // 다크 블루 - 호버/액티브 상태
    secondary: '#6C5CE7',    // 보조 보라색 - 보조 액션
    accent: '#00D4FF',       // 액센트 시안 - 하이라이트
  }
}
```

#### 시맨틱 색상
```javascript
const semantic = {
  success: '#10B981',  // 성공, 완료 상태
  warning: '#F59E0B',  // 경고, 주의 필요
  error: '#EF4444',    // 에러, 위험 상태
  info: '#3B82F6',     // 정보, 안내 메시지
}
```

#### 프로젝트 단계별 색상
```javascript
const projectPhases = {
  planning: '#3B82F6',      // 기획
  production: '#F59E0B',    // 제작
  postProduction: '#8B5CF6', // 후반작업
  review: '#06B6D4',        // 검토
  completed: '#10B981',     // 완료
}
```

### 1.2 타이포그래피 스케일

```javascript
const typography = {
  fontFamily: {
    primary: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    mono: "'JetBrains Mono', 'Courier New', monospace",
  },
  
  fontSize: {
    xs: '0.75rem',    // 12px - 캡션, 라벨
    sm: '0.875rem',   // 14px - 보조 텍스트
    base: '1rem',     // 16px - 본문
    lg: '1.125rem',   // 18px - 서브헤딩
    xl: '1.25rem',    // 20px - 헤딩
    '2xl': '1.5rem',  // 24px - 페이지 타이틀
    '3xl': '1.875rem', // 30px - 섹션 타이틀
    '4xl': '2.25rem', // 36px - 히어로 타이틀
  },
  
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  }
}
```

### 1.3 간격 시스템 (Spacing System)

```javascript
const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
}
```

### 1.4 그림자 시스템 (Shadow System)

```javascript
const shadows = {
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  none: 'none',
}
```

### 1.5 보더 시스템 (Border System)

```javascript
const borders = {
  radius: {
    none: '0',
    sm: '0.125rem',  // 2px
    md: '0.375rem',  // 6px
    lg: '0.5rem',    // 8px
    xl: '0.75rem',   // 12px
    '2xl': '1rem',   // 16px
    '3xl': '1.5rem', // 24px
    full: '9999px',
  },
  
  width: {
    0: '0',
    1: '1px',
    2: '2px',
    4: '4px',
    8: '8px',
  }
}
```

## 🧩 2. 핵심 UI 컴포넌트 목록

### 우선순위 1 - 기초 컴포넌트 (Foundation)
1. **Button** - 모든 버튼 액션의 기초
2. **Input** - 텍스트 입력 필드
3. **Select** - 드롭다운 선택
4. **Checkbox** - 체크박스
5. **Radio** - 라디오 버튼
6. **Switch** - 토글 스위치
7. **Typography** - 텍스트 스타일링

### 우선순위 2 - 레이아웃 컴포넌트 (Layout)
1. **Container** - 콘텐츠 컨테이너
2. **Grid** - 그리드 레이아웃
3. **Stack** - 수직/수평 스택
4. **Card** - 카드 컨테이너
5. **Modal** - 모달 다이얼로그
6. **Drawer** - 사이드 드로어
7. **Sidebar** - 네비게이션 사이드바

### 우선순위 3 - 피드백 컴포넌트 (Feedback)
1. **Alert** - 알림 메시지
2. **Toast** - 토스트 알림
3. **Progress** - 진행률 표시
4. **Skeleton** - 로딩 스켈레톤
5. **Spinner** - 로딩 스피너
6. **Empty** - 빈 상태 표시

### 우선순위 4 - 데이터 컴포넌트 (Data Display)
1. **Table** - 데이터 테이블
2. **List** - 리스트 뷰
3. **Avatar** - 사용자 아바타
4. **Badge** - 상태 배지
5. **Tag** - 태그 라벨
6. **Timeline** - 타임라인
7. **Tooltip** - 툴팁

### 우선순위 5 - 비즈니스 컴포넌트 (Business)
1. **ProjectCard** - 프로젝트 카드
2. **FeedbackItem** - 피드백 아이템
3. **VideoPlayer** - 비디오 플레이어
4. **PlanningWizard** - 기획 마법사
5. **Calendar** - 일정 캘린더
6. **GanttChart** - 간트 차트

## 📱 3. 레이아웃 시스템

### 3.1 반응형 브레이크포인트

```javascript
const breakpoints = {
  xs: '0px',      // 모바일 세로
  sm: '640px',    // 모바일 가로
  md: '768px',    // 태블릿 세로
  lg: '1024px',   // 태블릿 가로, 작은 노트북
  xl: '1280px',   // 데스크톱
  '2xl': '1536px', // 대형 데스크톱
}
```

### 3.2 그리드 시스템

```javascript
const grid = {
  columns: 12,
  gap: {
    xs: '1rem',
    sm: '1.5rem',
    md: '2rem',
    lg: '2.5rem',
  },
  container: {
    xs: '100%',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  }
}
```

### 3.3 레이아웃 패턴

#### 대시보드 레이아웃
```
┌─────────────────────────────────────┐
│          Header (64px)              │
├────────┬────────────────────────────┤
│Sidebar │      Main Content          │
│(240px) │     (Fluid Width)          │
│        │                            │
│        │                            │
└────────┴────────────────────────────┘
```

#### 프로젝트 뷰 레이아웃
```
┌─────────────────────────────────────┐
│     Project Header (120px)          │
├─────────────────────────────────────┤
│  Tab Navigation (48px)              │
├─────────────────────────────────────┤
│                                     │
│     Content Area (Fluid)            │
│                                     │
└─────────────────────────────────────┘
```

## ♿ 4. 접근성 가이드라인

### 4.1 색상 대비
- **WCAG AA 기준**: 일반 텍스트 4.5:1, 큰 텍스트 3:1
- **WCAG AAA 기준**: 일반 텍스트 7:1, 큰 텍스트 4.5:1
- 모든 인터랙티브 요소는 최소 AA 기준 충족

### 4.2 키보드 네비게이션
- 모든 인터랙티브 요소는 Tab 키로 접근 가능
- 포커스 표시자 명확하게 표시 (2px solid #1631F8)
- Escape 키로 모달/드로어 닫기
- 화살표 키로 메뉴 탐색

### 4.3 스크린 리더 지원
- 의미있는 alt 텍스트 제공
- ARIA 라벨 및 설명 사용
- 랜드마크 역할 적절히 사용
- 동적 콘텐츠 변경 알림 (aria-live)

### 4.4 모션 설정
- prefers-reduced-motion 미디어 쿼리 지원
- 모션 감소 시 애니메이션 최소화
- 자동 재생 비디오 일시정지 옵션

## ⚡ 5. 성능 최적화 전략

### 5.1 CSS 최적화
- **Critical CSS**: 초기 뷰포트에 필요한 CSS만 인라인
- **PurgeCSS**: 사용하지 않는 CSS 제거
- **CSS Modules**: 스코프 격리 및 트리 쉐이킹
- **PostCSS**: 자동 프리픽싱 및 최적화

### 5.2 컴포넌트 최적화
- **Code Splitting**: 라우트별 동적 임포트
- **Lazy Loading**: 뷰포트 외부 컴포넌트 지연 로드
- **Memoization**: React.memo, useMemo 활용
- **Virtual Scrolling**: 긴 리스트 가상화

### 5.3 이미지 최적화
- **Next.js Image**: 자동 최적화 및 lazy loading
- **WebP 포맷**: 자동 포맷 변환
- **Responsive Images**: srcset 활용
- **Blur Placeholder**: 로딩 중 블러 처리

### 5.4 번들 최적화
- **Tree Shaking**: 사용하지 않는 코드 제거
- **Minification**: JS/CSS 압축
- **Compression**: Gzip/Brotli 압축
- **CDN**: 정적 자산 CDN 배포

## 📊 6. 성능 목표

### Core Web Vitals 목표
- **LCP (Largest Contentful Paint)**: < 2.5초
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **TTFB (Time to First Byte)**: < 600ms

### 번들 크기 목표
- **Initial JS**: < 200KB (gzipped)
- **Initial CSS**: < 50KB (gzipped)
- **Total Page Weight**: < 1MB
- **Code Coverage**: > 60%

## 🔄 7. 마이그레이션 전략

### Phase 1: 기초 설정 (Week 1)
1. Tailwind CSS 설치 및 설정
2. 디자인 토큰 마이그레이션
3. PostCSS 파이프라인 구축
4. 기초 컴포넌트 10개 구현

### Phase 2: 컴포넌트 구축 (Week 2)
1. 레이아웃 컴포넌트 구현
2. 피드백 컴포넌트 구현
3. Storybook 설정
4. 컴포넌트 문서화

### Phase 3: 통합 및 최적화 (Week 3)
1. 비즈니스 컴포넌트 구현
2. 기존 페이지 마이그레이션
3. 성능 최적화
4. 접근성 테스트

### Phase 4: 배포 및 모니터링 (Week 4)
1. 프로덕션 배포
2. 성능 모니터링
3. 사용자 피드백 수집
4. 지속적 개선

## 📚 8. 컴포넌트 구현 가이드

### 컴포넌트 구조
```typescript
interface ComponentProps {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  className?: string
  children?: React.ReactNode
}

const Component: React.FC<ComponentProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  className,
  children
}) => {
  // 구현
}
```

### 스타일 가이드
```javascript
// Tailwind 클래스 조합
const baseClasses = 'inline-flex items-center justify-center'
const variantClasses = {
  primary: 'bg-brand-primary text-white hover:bg-brand-primaryDark',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
  danger: 'bg-red-600 text-white hover:bg-red-700'
}
const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg'
}
```

## 🎯 결론

VideoPlanet의 디자인 시스템은 일관성, 확장성, 성능을 핵심 가치로 합니다. 
체계적인 토큰 시스템과 컴포넌트 라이브러리를 통해 개발 효율성을 높이고, 
사용자에게 일관된 경험을 제공합니다.

### 핵심 성공 지표
- 개발 속도 40% 향상
- 디자인 일관성 100% 달성
- Core Web Vitals 모든 지표 "Good" 달성
- 접근성 WCAG AA 준수