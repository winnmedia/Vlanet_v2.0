# VideoPlanet UI 컴포넌트 구현 가이드

## 📦 컴포넌트 구현 우선순위 및 상세 스펙

### 🎯 Phase 1: 기초 컴포넌트 (Week 1, Days 1-3)

#### 1. Button Component
```typescript
// components/ui/Button.tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'link'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  fullWidth?: boolean
  loading?: boolean
  disabled?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  className?: string
  children: React.ReactNode
}

// 사용 예시
<Button 
  variant="primary"
  size="md"
  leftIcon={<PlusIcon />}
  loading={isSubmitting}
>
  새 프로젝트 만들기
</Button>
```

#### 2. Input Component
```typescript
// components/ui/Input.tsx
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'filled' | 'ghost'
  state?: 'default' | 'error' | 'success' | 'warning'
  label?: string
  placeholder?: string
  helperText?: string
  errorMessage?: string
  leftAddon?: React.ReactNode
  rightAddon?: React.ReactNode
  prefix?: React.ReactNode
  suffix?: React.ReactNode
  disabled?: boolean
  required?: boolean
  value?: string
  onChange?: (value: string) => void
}

// 사용 예시
<Input
  label="프로젝트 이름"
  placeholder="새로운 프로젝트 이름을 입력하세요"
  helperText="한글, 영문, 숫자 조합 가능"
  required
  state={errors.name ? 'error' : 'default'}
  errorMessage={errors.name}
/>
```

#### 3. Select Component
```typescript
// components/ui/Select.tsx
interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
  icon?: React.ReactNode
}

interface SelectProps {
  options: SelectOption[]
  value?: string | number
  defaultValue?: string | number
  placeholder?: string
  label?: string
  size?: 'sm' | 'md' | 'lg'
  multiple?: boolean
  searchable?: boolean
  clearable?: boolean
  disabled?: boolean
  loading?: boolean
  onChange?: (value: string | number | string[] | number[]) => void
}

// 사용 예시
<Select
  label="프로젝트 상태"
  options={[
    { value: 'planning', label: '기획중', icon: <PlanIcon /> },
    { value: 'production', label: '제작중', icon: <ProductionIcon /> },
    { value: 'completed', label: '완료', icon: <CompleteIcon /> }
  ]}
  searchable
  clearable
/>
```

#### 4. Checkbox Component
```typescript
// components/ui/Checkbox.tsx
interface CheckboxProps {
  checked?: boolean
  defaultChecked?: boolean
  indeterminate?: boolean
  disabled?: boolean
  label?: string
  description?: string
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  onChange?: (checked: boolean) => void
}

// 사용 예시
<Checkbox
  label="이용약관 동의"
  description="서비스 이용약관에 동의합니다"
  required
/>
```

#### 5. Radio Component
```typescript
// components/ui/Radio.tsx
interface RadioOption {
  value: string | number
  label: string
  description?: string
  disabled?: boolean
}

interface RadioGroupProps {
  options: RadioOption[]
  value?: string | number
  defaultValue?: string | number
  name: string
  label?: string
  orientation?: 'horizontal' | 'vertical'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onChange?: (value: string | number) => void
}

// 사용 예시
<RadioGroup
  label="공개 설정"
  name="visibility"
  options={[
    { value: 'public', label: '전체 공개' },
    { value: 'private', label: '비공개' },
    { value: 'team', label: '팀 멤버만' }
  ]}
/>
```

### 🎯 Phase 2: 레이아웃 컴포넌트 (Week 1, Days 4-5)

#### 6. Card Component
```typescript
// components/ui/Card.tsx
interface CardProps {
  variant?: 'elevated' | 'outlined' | 'filled'
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  hoverable?: boolean
  clickable?: boolean
  selected?: boolean
  header?: React.ReactNode
  footer?: React.ReactNode
  media?: {
    type: 'image' | 'video'
    src: string
    alt?: string
    position?: 'top' | 'left' | 'right'
  }
  actions?: React.ReactNode[]
  className?: string
  children: React.ReactNode
}

// 사용 예시
<Card
  variant="elevated"
  hoverable
  header={<CardHeader title="프로젝트 A" subtitle="진행중" />}
  media={{ type: 'image', src: '/thumbnail.jpg' }}
  footer={
    <CardActions>
      <Button size="sm">편집</Button>
      <Button size="sm" variant="ghost">삭제</Button>
    </CardActions>
  }
>
  프로젝트 내용...
</Card>
```

#### 7. Modal Component
```typescript
// components/ui/Modal.tsx
interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  description?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closeOnOverlayClick?: boolean
  closeOnEsc?: boolean
  showCloseButton?: boolean
  footer?: React.ReactNode
  className?: string
  children: React.ReactNode
}

// 사용 예시
<Modal
  open={isOpen}
  onClose={handleClose}
  title="프로젝트 삭제"
  description="정말로 이 프로젝트를 삭제하시겠습니까?"
  footer={
    <>
      <Button variant="ghost" onClick={handleClose}>취소</Button>
      <Button variant="danger" onClick={handleDelete}>삭제</Button>
    </>
  }
>
  삭제된 프로젝트는 복구할 수 없습니다.
</Modal>
```

#### 8. Grid System
```typescript
// components/layout/Grid.tsx
interface GridProps {
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 12
  gap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  responsive?: {
    xs?: number
    sm?: number
    md?: number
    lg?: number
    xl?: number
  }
  alignItems?: 'start' | 'center' | 'end' | 'stretch'
  justifyItems?: 'start' | 'center' | 'end' | 'stretch'
  className?: string
  children: React.ReactNode
}

// 사용 예시
<Grid cols={3} gap="md" responsive={{ xs: 1, md: 2, lg: 3 }}>
  <ProjectCard />
  <ProjectCard />
  <ProjectCard />
</Grid>
```

### 🎯 Phase 3: 피드백 컴포넌트 (Week 2, Days 1-2)

#### 9. Toast Component
```typescript
// components/ui/Toast.tsx
interface ToastProps {
  type?: 'success' | 'error' | 'warning' | 'info'
  title: string
  description?: string
  duration?: number
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right'
  action?: {
    label: string
    onClick: () => void
  }
  onClose?: () => void
}

// 사용 예시
toast.success({
  title: '저장 완료',
  description: '프로젝트가 성공적으로 저장되었습니다.',
  duration: 3000
})
```

#### 10. Alert Component
```typescript
// components/ui/Alert.tsx
interface AlertProps {
  type?: 'success' | 'error' | 'warning' | 'info'
  variant?: 'filled' | 'outlined' | 'light'
  title?: string
  description?: string
  icon?: React.ReactNode | boolean
  closable?: boolean
  action?: React.ReactNode
  onClose?: () => void
  className?: string
  children?: React.ReactNode
}

// 사용 예시
<Alert
  type="warning"
  title="주의사항"
  closable
>
  프로젝트 마감일이 3일 남았습니다.
</Alert>
```

### 🎯 Phase 4: 데이터 표시 컴포넌트 (Week 2, Days 3-4)

#### 11. Table Component
```typescript
// components/ui/Table.tsx
interface Column<T> {
  key: string
  title: string
  dataIndex: keyof T
  width?: number | string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  filterable?: boolean
  render?: (value: any, record: T, index: number) => React.ReactNode
}

interface TableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  pagination?: {
    current: number
    pageSize: number
    total: number
    onChange: (page: number, pageSize: number) => void
  }
  selection?: {
    type: 'checkbox' | 'radio'
    selectedKeys: string[]
    onChange: (selectedKeys: string[]) => void
  }
  rowKey: keyof T
  onRow?: (record: T) => object
  className?: string
}

// 사용 예시
<Table
  columns={[
    { key: 'name', title: '프로젝트명', dataIndex: 'name', sortable: true },
    { key: 'status', title: '상태', dataIndex: 'status', render: (status) => <StatusBadge status={status} /> },
    { key: 'date', title: '마감일', dataIndex: 'dueDate', align: 'center' }
  ]}
  data={projects}
  rowKey="id"
  pagination={{
    current: 1,
    pageSize: 10,
    total: 100,
    onChange: handlePageChange
  }}
/>
```

#### 12. Badge Component
```typescript
// components/ui/Badge.tsx
interface BadgeProps {
  variant?: 'solid' | 'outlined' | 'light'
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  dot?: boolean
  count?: number
  showZero?: boolean
  max?: number
  offset?: [number, number]
  className?: string
  children?: React.ReactNode
}

// 사용 예시
<Badge count={5} color="danger">
  <BellIcon />
</Badge>

<Badge variant="light" color="success">
  진행중
</Badge>
```

### 🎯 Phase 5: 비즈니스 컴포넌트 (Week 2, Day 5 - Week 3)

#### 13. ProjectCard Component
```typescript
// components/business/ProjectCard.tsx
interface ProjectCardProps {
  project: {
    id: string
    title: string
    description?: string
    thumbnail?: string
    status: 'planning' | 'production' | 'post-production' | 'review' | 'completed'
    progress: number
    dueDate: Date
    members: User[]
    tags?: string[]
  }
  variant?: 'grid' | 'list'
  actions?: boolean
  onEdit?: () => void
  onDelete?: () => void
  onClick?: () => void
}

// 사용 예시
<ProjectCard
  project={projectData}
  variant="grid"
  actions
  onClick={handleProjectClick}
/>
```

#### 14. FeedbackItem Component
```typescript
// components/business/FeedbackItem.tsx
interface FeedbackItemProps {
  feedback: {
    id: string
    user: User
    content: string
    timestamp: number // 비디오 타임스탬프
    createdAt: Date
    status: 'pending' | 'in-progress' | 'resolved' | 'rejected'
    replies?: FeedbackReply[]
    attachments?: Attachment[]
  }
  editable?: boolean
  onReply?: (content: string) => void
  onStatusChange?: (status: string) => void
  onEdit?: (content: string) => void
  onDelete?: () => void
}

// 사용 예시
<FeedbackItem
  feedback={feedbackData}
  editable={isOwner}
  onReply={handleReply}
  onStatusChange={handleStatusChange}
/>
```

#### 15. VideoPlayer Component
```typescript
// components/business/VideoPlayer.tsx
interface VideoPlayerProps {
  src: string
  poster?: string
  autoplay?: boolean
  controls?: boolean
  loop?: boolean
  muted?: boolean
  playbackRate?: number
  volume?: number
  currentTime?: number
  markers?: {
    time: number
    label: string
    color?: string
  }[]
  onTimeUpdate?: (time: number) => void
  onMarkerClick?: (marker: any) => void
  onPlay?: () => void
  onPause?: () => void
  onEnded?: () => void
  className?: string
}

// 사용 예시
<VideoPlayer
  src="/video.mp4"
  poster="/thumbnail.jpg"
  markers={feedbackMarkers}
  onTimeUpdate={handleTimeUpdate}
  onMarkerClick={handleMarkerClick}
/>
```

## 🎨 스타일링 가이드라인

### Tailwind 클래스 조합 패턴
```typescript
// utils/cn.ts - 클래스 결합 유틸리티
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 컴포넌트에서 사용
const buttonClasses = cn(
  // 기본 스타일
  'inline-flex items-center justify-center rounded-md font-medium transition-colors',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
  'disabled:pointer-events-none disabled:opacity-50',
  
  // 변형별 스타일
  variants[variant],
  
  // 크기별 스타일
  sizes[size],
  
  // 조건부 스타일
  fullWidth && 'w-full',
  loading && 'cursor-wait',
  
  // 사용자 정의 클래스
  className
)
```

### 컴포넌트 파일 구조
```
components/
├── ui/                    # 기초 UI 컴포넌트
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.stories.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   ├── Input/
│   ├── Select/
│   └── ...
├── layout/               # 레이아웃 컴포넌트
│   ├── Grid/
│   ├── Container/
│   └── ...
├── business/            # 비즈니스 로직 컴포넌트
│   ├── ProjectCard/
│   ├── FeedbackItem/
│   └── ...
└── index.ts            # 통합 export
```

## 🧪 테스트 전략

### 단위 테스트
```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
  
  it('handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  it('is disabled when loading', () => {
    render(<Button loading>Click me</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

### Storybook 스토리
```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
}

export const WithIcon: Story = {
  args: {
    variant: 'primary',
    leftIcon: <PlusIcon />,
    children: 'Add Project',
  },
}

export const Loading: Story = {
  args: {
    loading: true,
    children: 'Loading...',
  },
}
```

## 📊 성능 최적화 체크리스트

### 컴포넌트 최적화
- [ ] React.memo 사용 (필요한 경우)
- [ ] useMemo/useCallback 적절히 활용
- [ ] 동적 import 활용 (큰 컴포넌트)
- [ ] 이미지 lazy loading
- [ ] 가상 스크롤링 (긴 리스트)

### 번들 최적화
- [ ] Tree shaking 가능한 export 구조
- [ ] 컴포넌트별 코드 스플리팅
- [ ] CSS-in-JS 최소화
- [ ] 불필요한 re-render 방지

### 접근성 체크리스트
- [ ] 키보드 네비게이션 지원
- [ ] ARIA 속성 적절히 사용
- [ ] 포커스 관리
- [ ] 스크린 리더 테스트
- [ ] 색상 대비 WCAG AA 준수

## 🚀 구현 일정

### Week 1 (Days 1-7)
- **Day 1-3**: 기초 컴포넌트 5개 구현
- **Day 4-5**: 레이아웃 컴포넌트 3개 구현
- **Day 6**: Storybook 설정 및 문서화
- **Day 7**: 테스트 작성 및 리뷰

### Week 2 (Days 8-14)
- **Day 8-9**: 피드백 컴포넌트 구현
- **Day 10-11**: 데이터 표시 컴포넌트 구현
- **Day 12-14**: 비즈니스 컴포넌트 3개 구현

### Week 3 (Days 15-21)
- **Day 15-17**: 나머지 비즈니스 컴포넌트
- **Day 18-19**: 기존 페이지 마이그레이션
- **Day 20**: 성능 최적화
- **Day 21**: 최종 테스트 및 배포 준비

## 📝 체크리스트

### 컴포넌트 완성도 체크
- [ ] TypeScript 타입 정의 완료
- [ ] Props 검증 및 기본값 설정
- [ ] 다양한 상태 처리 (loading, error, empty)
- [ ] 반응형 디자인 적용
- [ ] 다크모드 지원
- [ ] Storybook 스토리 작성
- [ ] 단위 테스트 작성
- [ ] 문서화 완료
- [ ] 접근성 검증
- [ ] 성능 최적화