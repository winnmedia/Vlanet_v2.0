# 🎨 VideoPlanet UI 구현 가이드
## 인증 시스템 & 프로젝트 CRUD 컴포넌트

## 📑 목차
1. [컴포넌트 계층 구조](#컴포넌트-계층-구조)
2. [인증 UI 컴포넌트](#인증-ui-컴포넌트)
3. [프로젝트 CRUD UI 컴포넌트](#프로젝트-crud-ui-컴포넌트)
4. [Tailwind 스타일링 가이드](#tailwind-스타일링-가이드)
5. [상태 관리 전략](#상태-관리-전략)
6. [애니메이션 및 트랜지션](#애니메이션-및-트랜지션)
7. [에러 및 로딩 상태 디자인](#에러-및-로딩-상태-디자인)
8. [반응형 디자인 패턴](#반응형-디자인-패턴)
9. [접근성 구현 가이드](#접근성-구현-가이드)
10. [Figma 디자인 시스템 연동](#figma-디자인-시스템-연동)

---

## 컴포넌트 계층 구조

### 전체 아키텍처
```
src/
├── components/
│   ├── auth/                    # 인증 관련 컴포넌트
│   │   ├── LoginForm/
│   │   ├── SignupForm/
│   │   ├── PasswordResetForm/
│   │   ├── SocialLoginButtons/
│   │   └── AuthGuard/
│   │
│   ├── projects/                # 프로젝트 CRUD 컴포넌트
│   │   ├── ProjectList/
│   │   ├── ProjectCard/
│   │   ├── ProjectGrid/
│   │   ├── ProjectCreateForm/
│   │   ├── ProjectEditForm/
│   │   ├── ProjectDeleteModal/
│   │   └── ProjectFilters/
│   │
│   ├── ui/                      # 기본 UI 컴포넌트
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Select/
│   │   ├── Card/
│   │   ├── Modal/
│   │   ├── Toast/
│   │   ├── Skeleton/
│   │   └── Badge/
│   │
│   └── layout/                  # 레이아웃 컴포넌트
│       ├── Container/
│       ├── Grid/
│       ├── Stack/
│       └── Sidebar/
│
├── hooks/                       # 커스텀 훅
│   ├── useAuth.ts
│   ├── useProjects.ts
│   ├── useForm.ts
│   └── useToast.ts
│
└── lib/                         # 유틸리티
    ├── cn.ts                    # 클래스명 유틸리티
    ├── validation.ts            # 검증 스키마
    └── animations.ts            # 애니메이션 설정
```

---

## 인증 UI 컴포넌트

### 1. 로그인 폼 컴포넌트

#### Props 인터페이스
```typescript
interface LoginFormProps {
  onSuccess?: (user: User) => void;
  onError?: (error: Error) => void;
  redirectTo?: string;
  showSocialLogin?: boolean;
  rememberMe?: boolean;
}
```

#### 컴포넌트 구현
```tsx
// components/auth/LoginForm/LoginForm.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, Mail, Lock, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/cn';

const loginSchema = z.object({
  email: z.string()
    .email('올바른 이메일 형식이 아닙니다')
    .min(1, '이메일을 입력해주세요'),
  password: z.string()
    .min(8, '비밀번호는 최소 8자 이상이어야 합니다')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 
      '비밀번호는 대소문자와 숫자를 포함해야 합니다'),
  rememberMe: z.boolean().optional()
});

export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onError,
  redirectTo = '/dashboard',
  showSocialLogin = true,
  rememberMe = true
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors, touchedFields },
    setError
  } = useForm({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur'
  });

  const onSubmit = async (data: z.infer<typeof loginSchema>) => {
    setIsLoading(true);
    try {
      // API 호출
      const response = await authAPI.login(data);
      onSuccess?.(response.user);
    } catch (error) {
      setError('root', {
        message: '이메일 또는 비밀번호가 올바르지 않습니다'
      });
      onError?.(error as Error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-md mx-auto"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* 이메일 입력 필드 */}
        <div className="space-y-2">
          <label 
            htmlFor="email" 
            className="block text-sm font-medium text-gray-700"
          >
            이메일
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              {...register('email')}
              type="email"
              id="email"
              className={cn(
                "w-full pl-10 pr-4 py-2.5 rounded-lg",
                "border transition-colors duration-200",
                "focus:outline-none focus:ring-2 focus:ring-offset-2",
                errors.email
                  ? "border-red-500 focus:ring-red-500"
                  : touchedFields.email
                  ? "border-green-500 focus:ring-green-500"
                  : "border-gray-300 focus:ring-brand-primary focus:border-brand-primary"
              )}
              placeholder="name@company.com"
              aria-invalid={!!errors.email}
              aria-describedby={errors.email ? "email-error" : undefined}
            />
            {errors.email && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                id="email-error"
                className="mt-1 text-sm text-red-500 flex items-center gap-1"
              >
                <AlertCircle className="w-4 h-4" />
                {errors.email.message}
              </motion.p>
            )}
          </div>
        </div>

        {/* 비밀번호 입력 필드 */}
        <div className="space-y-2">
          <label 
            htmlFor="password" 
            className="block text-sm font-medium text-gray-700"
          >
            비밀번호
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              {...register('password')}
              type={showPassword ? 'text' : 'password'}
              id="password"
              className={cn(
                "w-full pl-10 pr-12 py-2.5 rounded-lg",
                "border transition-colors duration-200",
                "focus:outline-none focus:ring-2 focus:ring-offset-2",
                errors.password
                  ? "border-red-500 focus:ring-red-500"
                  : "border-gray-300 focus:ring-brand-primary focus:border-brand-primary"
              )}
              placeholder="••••••••"
              aria-invalid={!!errors.password}
              aria-describedby={errors.password ? "password-error" : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              aria-label={showPassword ? "비밀번호 숨기기" : "비밀번호 보기"}
            >
              {showPassword ? (
                <EyeOff className="w-5 h-5" />
              ) : (
                <Eye className="w-5 h-5" />
              )}
            </button>
            {errors.password && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                id="password-error"
                className="mt-1 text-sm text-red-500 flex items-center gap-1"
              >
                <AlertCircle className="w-4 h-4" />
                {errors.password.message}
              </motion.p>
            )}
          </div>
        </div>

        {/* 기억하기 & 비밀번호 찾기 */}
        {rememberMe && (
          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                {...register('rememberMe')}
                type="checkbox"
                className="w-4 h-4 text-brand-primary border-gray-300 rounded focus:ring-brand-primary"
              />
              <span className="ml-2 text-sm text-gray-600">로그인 유지</span>
            </label>
            <a 
              href="/reset-password" 
              className="text-sm text-brand-primary hover:text-brand-primary-dark"
            >
              비밀번호 찾기
            </a>
          </div>
        )}

        {/* 전체 폼 에러 */}
        {errors.root && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-4 bg-red-50 border border-red-200 rounded-lg"
          >
            <p className="text-sm text-red-600 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {errors.root.message}
            </p>
          </motion.div>
        )}

        {/* 로그인 버튼 */}
        <button
          type="submit"
          disabled={isLoading}
          className={cn(
            "w-full py-3 px-4 rounded-lg font-medium",
            "bg-gradient-to-r from-brand-primary to-brand-primary-dark",
            "text-white shadow-lg shadow-brand-primary/25",
            "hover:shadow-xl hover:shadow-brand-primary/30",
            "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-primary",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "transform transition-all duration-200 hover:-translate-y-0.5"
          )}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              로그인 중...
            </span>
          ) : (
            '로그인'
          )}
        </button>

        {/* 소셜 로그인 */}
        {showSocialLogin && (
          <>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">또는</span>
              </div>
            </div>
            
            <SocialLoginButtons />
          </>
        )}

        {/* 회원가입 링크 */}
        <p className="text-center text-sm text-gray-600">
          아직 계정이 없으신가요?{' '}
          <a 
            href="/signup" 
            className="font-medium text-brand-primary hover:text-brand-primary-dark"
          >
            회원가입
          </a>
        </p>
      </form>
    </motion.div>
  );
};
```

### 2. 회원가입 폼 컴포넌트

#### Props 인터페이스
```typescript
interface SignupFormProps {
  onSuccess?: (user: User) => void;
  onError?: (error: Error) => void;
  requireEmailVerification?: boolean;
  termsUrl?: string;
  privacyUrl?: string;
}
```

### 3. 비밀번호 재설정 컴포넌트

#### Props 인터페이스
```typescript
interface PasswordResetFormProps {
  token?: string;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  step?: 'request' | 'reset';
}
```

---

## 프로젝트 CRUD UI 컴포넌트

### 1. 프로젝트 카드 컴포넌트

#### Props 인터페이스
```typescript
interface ProjectCardProps {
  project: Project;
  variant?: 'grid' | 'list';
  showActions?: boolean;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
  onClick?: (project: Project) => void;
  className?: string;
}
```

#### 컴포넌트 구현
```tsx
// components/projects/ProjectCard/ProjectCard.tsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  MoreVertical, 
  Edit, 
  Trash2, 
  Users, 
  Calendar, 
  Clock,
  Film,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { Badge } from '@/components/ui/Badge';
import { Dropdown } from '@/components/ui/Dropdown';
import { Avatar } from '@/components/ui/Avatar';

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  variant = 'grid',
  showActions = true,
  onEdit,
  onDelete,
  onClick,
  className
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  const statusColors = {
    planning: 'bg-phase-planning-light text-phase-planning-dark',
    production: 'bg-phase-production-light text-phase-production-dark',
    'post-production': 'bg-phase-post-production-light text-phase-post-production-dark',
    review: 'bg-phase-review-light text-phase-review-dark',
    completed: 'bg-phase-completed-light text-phase-completed-dark'
  };

  const statusLabels = {
    planning: '기획',
    production: '제작',
    'post-production': '후반작업',
    review: '검토',
    completed: '완료'
  };

  if (variant === 'list') {
    return (
      <motion.div
        whileHover={{ x: 4 }}
        className={cn(
          "flex items-center gap-4 p-4 bg-white rounded-lg border",
          "hover:shadow-md transition-all duration-200",
          "cursor-pointer",
          className
        )}
        onClick={() => onClick?.(project)}
      >
        {/* 썸네일 */}
        <div className="w-20 h-20 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
          {project.thumbnail ? (
            <img 
              src={project.thumbnail} 
              alt={project.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Film className="w-8 h-8 text-gray-400" />
            </div>
          )}
        </div>

        {/* 프로젝트 정보 */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">
            {project.title}
          </h3>
          <p className="text-sm text-gray-500 line-clamp-1 mt-1">
            {project.description}
          </p>
          <div className="flex items-center gap-4 mt-2">
            <Badge className={cn(statusColors[project.status], 'text-xs')}>
              {statusLabels[project.status]}
            </Badge>
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {new Date(project.deadline).toLocaleDateString('ko-KR')}
            </span>
          </div>
        </div>

        {/* 팀 멤버 */}
        <div className="flex -space-x-2">
          {project.members.slice(0, 3).map((member) => (
            <Avatar
              key={member.id}
              src={member.avatar}
              name={member.name}
              size="sm"
              className="border-2 border-white"
            />
          ))}
          {project.members.length > 3 && (
            <div className="w-8 h-8 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center">
              <span className="text-xs text-gray-600">
                +{project.members.length - 3}
              </span>
            </div>
          )}
        </div>

        {/* 액션 메뉴 */}
        {showActions && (
          <Dropdown>
            <Dropdown.Trigger>
              <button className="p-2 hover:bg-gray-100 rounded-lg">
                <MoreVertical className="w-4 h-4 text-gray-500" />
              </button>
            </Dropdown.Trigger>
            <Dropdown.Content>
              <Dropdown.Item onClick={() => onEdit?.(project)}>
                <Edit className="w-4 h-4 mr-2" />
                수정
              </Dropdown.Item>
              <Dropdown.Item 
                onClick={() => onDelete?.(project)}
                className="text-red-600"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                삭제
              </Dropdown.Item>
            </Dropdown.Content>
          </Dropdown>
        )}
      </motion.div>
    );
  }

  // Grid 뷰
  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={cn(
        "bg-white rounded-xl overflow-hidden",
        "border border-gray-200 hover:border-brand-primary/30",
        "shadow-sm hover:shadow-xl transition-all duration-200",
        "cursor-pointer group",
        className
      )}
      onClick={() => onClick?.(project)}
    >
      {/* 썸네일 영역 */}
      <div className="relative aspect-video bg-gray-100 overflow-hidden">
        {project.thumbnail ? (
          <img 
            src={project.thumbnail} 
            alt={project.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
            <Film className="w-12 h-12 text-gray-400" />
          </div>
        )}
        
        {/* 상태 배지 */}
        <div className="absolute top-3 left-3">
          <Badge className={cn(statusColors[project.status], 'shadow-md')}>
            {statusLabels[project.status]}
          </Badge>
        </div>

        {/* 액션 버튼 (호버 시 표시) */}
        {showActions && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute top-3 right-3"
          >
            <Dropdown>
              <Dropdown.Trigger>
                <button className="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-md hover:bg-white">
                  <MoreVertical className="w-4 h-4 text-gray-700" />
                </button>
              </Dropdown.Trigger>
              <Dropdown.Content>
                <Dropdown.Item onClick={(e) => {
                  e.stopPropagation();
                  onEdit?.(project);
                }}>
                  <Edit className="w-4 h-4 mr-2" />
                  수정
                </Dropdown.Item>
                <Dropdown.Item 
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete?.(project);
                  }}
                  className="text-red-600"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  삭제
                </Dropdown.Item>
              </Dropdown.Content>
            </Dropdown>
          </motion.div>
        )}

        {/* 진행률 바 */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10">
          <motion.div 
            className="h-full bg-gradient-to-r from-brand-primary to-brand-accent"
            initial={{ width: 0 }}
            animate={{ width: `${project.progress}%` }}
            transition={{ duration: 0.5, delay: 0.2 }}
          />
        </div>
      </div>

      {/* 콘텐츠 영역 */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-1 group-hover:text-brand-primary transition-colors">
          {project.title}
        </h3>
        
        <p className="mt-2 text-sm text-gray-500 line-clamp-2">
          {project.description}
        </p>

        {/* 메타 정보 */}
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(project.deadline).toLocaleDateString('ko-KR')}
            </span>
            <span className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              {project.members.length}
            </span>
          </div>

          {/* 완료 상태 표시 */}
          {project.status === 'completed' && (
            <CheckCircle className="w-5 h-5 text-green-500" />
          )}
        </div>

        {/* 태그 */}
        {project.tags && project.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {project.tags.slice(0, 3).map((tag) => (
              <span 
                key={tag}
                className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                #{tag}
              </span>
            ))}
            {project.tags.length > 3 && (
              <span className="px-2 py-0.5 text-gray-500 text-xs">
                +{project.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};
```

### 2. 프로젝트 생성/수정 폼

#### Props 인터페이스
```typescript
interface ProjectFormProps {
  project?: Project;
  mode: 'create' | 'edit';
  onSubmit: (data: ProjectFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}
```

### 3. 프로젝트 목록 컴포넌트

#### Props 인터페이스
```typescript
interface ProjectListProps {
  projects: Project[];
  viewMode?: 'grid' | 'list';
  loading?: boolean;
  emptyMessage?: string;
  onProjectClick?: (project: Project) => void;
  onProjectEdit?: (project: Project) => void;
  onProjectDelete?: (project: Project) => void;
  className?: string;
}
```

---

## Tailwind 스타일링 가이드

### 1. 색상 체계
```javascript
// 브랜드 색상 (tailwind.config.js에 정의)
const colors = {
  brand: {
    primary: '#1631F8',        // 주요 액션
    'primary-dark': '#0F23C9', // 호버/액티브
    secondary: '#6C5CE7',      // 보조 액션
    accent: '#00D4FF'          // 강조
  },
  
  // 시맨틱 색상
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6'
}
```

### 2. 컴포넌트별 스타일 패턴

#### 버튼 스타일
```typescript
const buttonVariants = {
  primary: `
    bg-gradient-to-r from-brand-primary to-brand-primary-dark
    text-white shadow-lg shadow-brand-primary/25
    hover:shadow-xl hover:shadow-brand-primary/30
    hover:-translate-y-0.5
  `,
  secondary: `
    bg-gray-100 text-gray-900
    hover:bg-gray-200
  `,
  danger: `
    bg-gradient-to-r from-red-600 to-red-700
    text-white shadow-lg shadow-red-600/25
    hover:shadow-xl hover:shadow-red-600/30
  `,
  ghost: `
    bg-transparent text-gray-700
    hover:bg-gray-100
  `
};

const buttonSizes = {
  xs: 'px-2.5 py-1 text-xs',
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
  xl: 'px-8 py-4 text-xl'
};
```

#### 입력 필드 스타일
```typescript
const inputVariants = {
  default: `
    border-gray-300 
    focus:border-brand-primary focus:ring-brand-primary
  `,
  error: `
    border-red-500 
    focus:border-red-500 focus:ring-red-500
  `,
  success: `
    border-green-500 
    focus:border-green-500 focus:ring-green-500
  `
};
```

### 3. 유틸리티 클래스 조합
```typescript
// lib/cn.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// 사용 예시
<div className={cn(
  "base-classes",
  condition && "conditional-classes",
  className // 외부에서 전달된 클래스
)} />
```

---

## 상태 관리 전략

### 1. Zustand 스토어 구조

#### 인증 스토어
```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(credentials);
          set({ 
            user: response.user, 
            isAuthenticated: true,
            isLoading: false 
          });
        } catch (error) {
          set({ 
            error: error.message,
            isLoading: false 
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
          set({ 
            user: null, 
            isAuthenticated: false 
          });
        } catch (error) {
          console.error('Logout failed:', error);
        }
      },

      clearError: () => set({ error: null })
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
);
```

#### 프로젝트 스토어
```typescript
// stores/projectStore.ts
interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  filters: ProjectFilters;
  viewMode: 'grid' | 'list';
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchProjects: (filters?: ProjectFilters) => Promise<void>;
  createProject: (data: CreateProjectData) => Promise<Project>;
  updateProject: (id: string, data: UpdateProjectData) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
  setViewMode: (mode: 'grid' | 'list') => void;
  setFilters: (filters: ProjectFilters) => void;
}
```

### 2. React Query 통합

```typescript
// hooks/useProjects.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useProjects = (filters?: ProjectFilters) => {
  return useQuery({
    queryKey: ['projects', filters],
    queryFn: () => projectAPI.getProjects(filters),
    staleTime: 5 * 60 * 1000, // 5분
    cacheTime: 10 * 60 * 1000 // 10분
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: projectAPI.createProject,
    onSuccess: (newProject) => {
      // 캐시 업데이트
      queryClient.setQueryData(['projects'], (old: Project[]) => {
        return [...old, newProject];
      });
    },
    // Optimistic Update
    onMutate: async (newProject) => {
      await queryClient.cancelQueries({ queryKey: ['projects'] });
      const previousProjects = queryClient.getQueryData(['projects']);
      
      queryClient.setQueryData(['projects'], (old: Project[]) => {
        return [...old, { ...newProject, id: 'temp-id' }];
      });
      
      return { previousProjects };
    },
    onError: (err, newProject, context) => {
      queryClient.setQueryData(['projects'], context.previousProjects);
    }
  });
};
```

---

## 애니메이션 및 트랜지션

### 1. Framer Motion 애니메이션

#### 페이지 전환 애니메이션
```typescript
// lib/animations.ts
export const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut'
    }
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: {
      duration: 0.3
    }
  }
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

export const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.6, -0.05, 0.01, 0.99]
    }
  }
};
```

#### 마이크로 인터랙션
```typescript
// 버튼 호버 애니메이션
export const buttonHover = {
  scale: 1.02,
  y: -2,
  transition: {
    duration: 0.2,
    ease: 'easeInOut'
  }
};

// 카드 호버 애니메이션
export const cardHover = {
  y: -8,
  shadow: '0 20px 40px rgba(0,0,0,0.15)',
  transition: {
    duration: 0.3,
    ease: 'easeOut'
  }
};
```

### 2. CSS 트랜지션

```css
/* 기본 트랜지션 클래스 */
.transition-base {
  @apply transition-all duration-200 ease-in-out;
}

.transition-colors {
  @apply transition-colors duration-200 ease-in-out;
}

.transition-transform {
  @apply transition-transform duration-300 ease-out;
}

/* 커스텀 트랜지션 */
.transition-bounce {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## 에러 및 로딩 상태 디자인

### 1. 로딩 상태 컴포넌트

#### 스켈레톤 로더
```tsx
// components/ui/Skeleton/ProjectCardSkeleton.tsx
export const ProjectCardSkeleton = () => {
  return (
    <div className="bg-white rounded-xl overflow-hidden border border-gray-200">
      {/* 썸네일 스켈레톤 */}
      <div className="aspect-video bg-gray-200 animate-shimmer" />
      
      {/* 콘텐츠 스켈레톤 */}
      <div className="p-4 space-y-3">
        <div className="h-5 bg-gray-200 rounded animate-shimmer" />
        <div className="space-y-2">
          <div className="h-3 bg-gray-200 rounded animate-shimmer" />
          <div className="h-3 bg-gray-200 rounded w-3/4 animate-shimmer" />
        </div>
        <div className="flex gap-2">
          <div className="h-6 w-16 bg-gray-200 rounded-full animate-shimmer" />
          <div className="h-6 w-20 bg-gray-200 rounded-full animate-shimmer" />
        </div>
      </div>
    </div>
  );
};
```

#### 스피너 컴포넌트
```tsx
// components/ui/Spinner/Spinner.tsx
interface SpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'brand-primary',
  className
}) => {
  const sizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className={cn('relative', sizes[size], className)}>
      <div className={cn(
        'absolute inset-0 rounded-full border-2 border-gray-200'
      )} />
      <div className={cn(
        'absolute inset-0 rounded-full border-2 border-t-transparent animate-spin',
        `border-${color}`
      )} />
    </div>
  );
};
```

### 2. 에러 상태 컴포넌트

```tsx
// components/ui/ErrorState/ErrorState.tsx
interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = '오류가 발생했습니다',
  message = '잠시 후 다시 시도해주세요',
  onRetry,
  className
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4',
        className
      )}
    >
      <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-4">
        <AlertCircle className="w-10 h-10 text-red-500" />
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>
      
      <p className="text-sm text-gray-500 text-center max-w-sm mb-6">
        {message}
      </p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-brand-primary text-white rounded-lg hover:bg-brand-primary-dark transition-colors"
        >
          다시 시도
        </button>
      )}
    </motion.div>
  );
};
```

### 3. 빈 상태 컴포넌트

```tsx
// components/ui/EmptyState/EmptyState.tsx
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className
}) => {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center py-16 px-4',
      className
    )}>
      {icon && (
        <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
          {icon}
        </div>
      )}
      
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {title}
      </h3>
      
      {description && (
        <p className="text-gray-500 text-center max-w-md mb-8">
          {description}
        </p>
      )}
      
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-3 bg-brand-primary text-white rounded-lg hover:bg-brand-primary-dark transition-colors flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          {action.label}
        </button>
      )}
    </div>
  );
};
```

---

## 반응형 디자인 패턴

### 1. 브레이크포인트 시스템
```javascript
// tailwind.config.js에 정의된 브레이크포인트
const breakpoints = {
  xs: '480px',   // 모바일 소형
  sm: '640px',   // 모바일 대형
  md: '768px',   // 태블릿 세로
  lg: '1024px',  // 태블릿 가로
  xl: '1280px',  // 데스크톱
  '2xl': '1536px' // 대형 데스크톱
};
```

### 2. 반응형 그리드 시스템

```tsx
// components/layout/ResponsiveGrid.tsx
interface ResponsiveGridProps {
  children: React.ReactNode;
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: string;
  className?: string;
}

export const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  cols = { xs: 1, sm: 2, md: 3, lg: 4 },
  gap = 'gap-4',
  className
}) => {
  const gridCols = cn(
    'grid',
    cols.xs && `grid-cols-${cols.xs}`,
    cols.sm && `sm:grid-cols-${cols.sm}`,
    cols.md && `md:grid-cols-${cols.md}`,
    cols.lg && `lg:grid-cols-${cols.lg}`,
    cols.xl && `xl:grid-cols-${cols.xl}`,
    gap,
    className
  );

  return <div className={gridCols}>{children}</div>;
};
```

### 3. 모바일 우선 컴포넌트

```tsx
// 모바일 우선 네비게이션
export const MobileFirstNav = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* 모바일 메뉴 버튼 (기본 표시, lg에서 숨김) */}
      <button 
        className="lg:hidden p-2"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Menu className="w-6 h-6" />
      </button>

      {/* 데스크톱 네비게이션 (기본 숨김, lg에서 표시) */}
      <nav className="hidden lg:flex items-center gap-6">
        {/* 네비게이션 아이템들 */}
      </nav>

      {/* 모바일 드로어 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            className="fixed inset-y-0 right-0 w-64 bg-white shadow-xl z-50 lg:hidden"
          >
            {/* 모바일 메뉴 콘텐츠 */}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
```

---

## 접근성 구현 가이드

### 1. ARIA 속성 활용

```tsx
// 접근성을 고려한 버튼 컴포넌트
interface AccessibleButtonProps {
  label: string;
  ariaLabel?: string;
  ariaPressed?: boolean;
  ariaExpanded?: boolean;
  ariaControls?: string;
  ariaDescribedBy?: string;
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  label,
  ariaLabel,
  ariaPressed,
  ariaExpanded,
  ariaControls,
  ariaDescribedBy,
  ...props
}) => {
  return (
    <button
      aria-label={ariaLabel || label}
      aria-pressed={ariaPressed}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      aria-describedby={ariaDescribedBy}
      {...props}
    >
      {label}
    </button>
  );
};
```

### 2. 키보드 네비게이션

```tsx
// 키보드 네비게이션을 지원하는 드롭다운
export const KeyboardNavigableDropdown = () => {
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const options = useRef<HTMLElement[]>([]);

  const handleKeyDown = (e: KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < options.current.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : options.current.length - 1
        );
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (selectedIndex >= 0) {
          options.current[selectedIndex]?.click();
        }
        break;
      case 'Escape':
        // 드롭다운 닫기
        break;
    }
  };

  return (
    <div role="listbox" onKeyDown={handleKeyDown}>
      {items.map((item, index) => (
        <div
          key={item.id}
          role="option"
          ref={el => options.current[index] = el}
          aria-selected={selectedIndex === index}
          tabIndex={selectedIndex === index ? 0 : -1}
        >
          {item.label}
        </div>
      ))}
    </div>
  );
};
```

### 3. 포커스 관리

```tsx
// 포커스 트랩 훅
export const useFocusTrap = (ref: RefObject<HTMLElement>) => {
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const focusableElements = element.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );
    
    const firstFocusable = focusableElements[0] as HTMLElement;
    const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable.focus();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable.focus();
        }
      }
    };

    element.addEventListener('keydown', handleKeyDown);
    firstFocusable?.focus();

    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  }, [ref]);
};
```

### 4. 스크린 리더 지원

```tsx
// 스크린 리더 전용 텍스트
export const ScreenReaderOnly = ({ children }: { children: React.ReactNode }) => {
  return (
    <span className="sr-only">
      {children}
    </span>
  );
};

// 라이브 리전 알림
export const LiveRegion = ({ message, priority = 'polite' }: {
  message: string;
  priority?: 'polite' | 'assertive';
}) => {
  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  );
};
```

---

## Figma 디자인 시스템 연동

### 1. 디자인 토큰 동기화

```javascript
// design-tokens/tokens.js
// Figma Tokens 플러그인과 동기화되는 토큰 파일
export const tokens = {
  colors: {
    brand: {
      primary: { value: '#1631F8' },
      primaryDark: { value: '#0F23C9' },
      secondary: { value: '#6C5CE7' },
      accent: { value: '#00D4FF' }
    }
  },
  spacing: {
    xs: { value: '0.25rem' },
    sm: { value: '0.5rem' },
    md: { value: '1rem' },
    lg: { value: '1.5rem' },
    xl: { value: '2rem' }
  },
  typography: {
    fontFamily: {
      sans: { value: 'Pretendard, -apple-system, sans-serif' },
      mono: { value: 'JetBrains Mono, monospace' }
    },
    fontSize: {
      xs: { value: '0.75rem' },
      sm: { value: '0.875rem' },
      base: { value: '1rem' },
      lg: { value: '1.125rem' },
      xl: { value: '1.25rem' }
    }
  },
  shadows: {
    sm: { value: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' },
    md: { value: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' },
    lg: { value: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }
  }
};
```

### 2. 컴포넌트 명명 규칙

```
Figma 컴포넌트 → React 컴포넌트 매핑

Figma: Button/Primary/Large
React: <Button variant="primary" size="lg" />

Figma: Card/Project/Grid
React: <ProjectCard variant="grid" />

Figma: Input/Text/Error
React: <Input type="text" state="error" />
```

### 3. Figma 변수와 CSS 변수 연동

```css
/* globals.css */
:root {
  /* Figma 변수와 1:1 매핑 */
  --color-brand-primary: #1631F8;
  --color-brand-primary-dark: #0F23C9;
  --color-brand-secondary: #6C5CE7;
  --color-brand-accent: #00D4FF;
  
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
}
```

### 4. Storybook과 Figma 연동

```typescript
// .storybook/preview.js
export const parameters = {
  design: {
    type: 'figma',
    url: 'https://www.figma.com/file/xxx/VideoPlanet-Design-System'
  },
  docs: {
    theme: customTheme,
  }
};

// Button.stories.tsx
export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button'
  },
  parameters: {
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/xxx/VideoPlanet?node-id=123:456'
    }
  }
};
```

### 5. 자동화 워크플로우

```json
// package.json
{
  "scripts": {
    "tokens:sync": "figma-tokens-sync",
    "tokens:build": "style-dictionary build",
    "design:export": "figma-export components",
    "design:assets": "figma-export assets"
  }
}
```

---

## 구현 체크리스트

### Phase 1: 기초 설정 (Day 1-2)
- [ ] Tailwind CSS 설정 및 커스터마이징
- [ ] 디자인 토큰 정의 및 CSS 변수 설정
- [ ] 기본 UI 컴포넌트 라이브러리 구조 설정
- [ ] Storybook 환경 구성
- [ ] 유틸리티 함수 (cn, validation) 구현

### Phase 2: 인증 UI (Day 3-4)
- [ ] LoginForm 컴포넌트 구현
- [ ] SignupForm 컴포넌트 구현
- [ ] PasswordResetForm 컴포넌트 구현
- [ ] SocialLoginButtons 컴포넌트 구현
- [ ] AuthGuard HOC 구현
- [ ] 인증 관련 상태 관리 (Zustand)

### Phase 3: 프로젝트 CRUD UI (Day 5-7)
- [ ] ProjectCard 컴포넌트 (Grid/List 뷰)
- [ ] ProjectList 컴포넌트
- [ ] ProjectCreateForm 컴포넌트
- [ ] ProjectEditForm 컴포넌트
- [ ] ProjectDeleteModal 컴포넌트
- [ ] ProjectFilters 컴포넌트
- [ ] 프로젝트 상태 관리 (Zustand + React Query)

### Phase 4: 공통 UI 컴포넌트 (Day 8-9)
- [ ] Button, Input, Select 컴포넌트
- [ ] Card, Modal, Drawer 컴포넌트
- [ ] Toast, Alert, Badge 컴포넌트
- [ ] Skeleton, Spinner 로딩 컴포넌트
- [ ] EmptyState, ErrorState 컴포넌트

### Phase 5: 반응형 & 접근성 (Day 10-11)
- [ ] 모든 컴포넌트 반응형 디자인 적용
- [ ] 모바일 터치 인터랙션 최적화
- [ ] ARIA 속성 및 시맨틱 마크업
- [ ] 키보드 네비게이션 구현
- [ ] 포커스 관리 및 스크린 리더 테스트

### Phase 6: 애니메이션 & 최적화 (Day 12-13)
- [ ] Framer Motion 애니메이션 적용
- [ ] 마이크로 인터랙션 구현
- [ ] 컴포넌트 lazy loading
- [ ] 이미지 최적화 (next/image)
- [ ] 번들 사이즈 최적화

### Phase 7: 통합 & 테스트 (Day 14)
- [ ] Figma 디자인 시스템 연동
- [ ] Storybook 문서화 완성
- [ ] E2E 테스트 시나리오 작성
- [ ] 접근성 자동 테스트
- [ ] 성능 프로파일링

---

## 성능 목표

### Core Web Vitals
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms  
- CLS (Cumulative Layout Shift): < 0.1
- INP (Interaction to Next Paint): < 200ms

### 컴포넌트 성능
- 초기 렌더링: < 50ms
- 리렌더링: < 16ms (60fps)
- 번들 크기: < 50KB per component
- 코드 커버리지: > 80%

---

## 결론

이 가이드는 VideoPlanet의 인증 시스템과 프로젝트 CRUD 기능을 위한 포괄적인 UI 구현 전략을 제공합니다. 모바일 우선 반응형 디자인, 접근성, 성능 최적화를 핵심 원칙으로 하여 사용자에게 최상의 경험을 제공하는 것을 목표로 합니다.

### 핵심 성공 요소
1. **일관된 디자인 시스템**: Tailwind CSS 기반의 체계적인 스타일링
2. **뛰어난 사용자 경험**: 직관적인 인터페이스와 부드러운 애니메이션
3. **완벽한 접근성**: WCAG 2.1 AA 기준 준수
4. **최적의 성능**: Core Web Vitals 목표 달성
5. **효율적인 개발**: 재사용 가능한 컴포넌트와 명확한 패턴

---

*작성일: 2025-01-09*  
*작성자: Sophia (UI Lead)*  
*버전: 1.0.0*