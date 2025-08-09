// ========================================
// 기본 타입 정의
// ========================================

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: APIError;
}

export interface APIError {
  message: string;
  code?: string;
  field?: string;
  details?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ========================================
// 사용자 관련 타입
// ========================================

export interface User {
  id: number;
  email: string;
  username?: string;
  nickname: string;
  profile_image?: string | null;
  company?: string | null;
  phone?: string | null;
  created_at?: string;
  email_verified?: boolean;
  login_method?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  tokens?: AuthTokens;
  access?: string;
  refresh?: string;
  access_token?: string;
  refresh_token?: string;
  vridge_session?: string;
  message?: string;
  status?: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  nickname: string;
  phone?: string;
  company?: string;
}

export interface SignupResponse {
  user: User;
  tokens: AuthTokens;
}

// ========================================
// 프로젝트 관련 타입
// ========================================

export type ProjectStatus = 
  | 'planning'    // 기획 중
  | 'production'  // 제작 중
  | 'review'      // 검토 중
  | 'completed'   // 완료
  | 'archived';   // 보관됨

export interface Project {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  status: ProjectStatus;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  owner: {
    id: number;
    nickname: string;
    email?: string;
  };
  members_count?: number;
  thumbnail?: string | null;
  progress?: number;
  tags?: string[];
}

export interface ProjectDetail extends Project {
  members: ProjectMember[];
  files: ProjectFile[];
}

export interface ProjectMember {
  id: number;
  nickname: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  avatar?: string;
  name?: string;
}

export interface ProjectFile {
  id: number;
  filename: string;
  file_url: string;
  uploaded_at: string;
}

export interface CreateProjectRequest {
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  status?: string;
  is_public?: boolean;
}

export interface UpdateProjectRequest extends Partial<CreateProjectRequest> {}

// ========================================
// 피드백 관련 타입
// ========================================

export type FeedbackStatus = 
  | 'pending'
  | 'in-progress'
  | 'resolved'
  | 'rejected';

export type FeedbackPriority = 
  | 'low'
  | 'medium'
  | 'high'
  | 'critical';

export interface Feedback {
  id: number;
  content: string;
  status: FeedbackStatus;
  priority: FeedbackPriority;
  timestamp: number;
  author: User;
  project_id: number;
  created_at: string;
  updated_at: string;
}

// ========================================
// UI 관련 타입
// ========================================

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface DropdownItem {
  id: string;
  label: string;
  icon?: React.ComponentType<any>;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export interface ToastOptions {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  description: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnOverlayClick?: boolean;
  showCloseButton?: boolean;
}

// ========================================
// 폼 관련 타입
// ========================================

export interface FormFieldProps {
  label?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  helpText?: string;
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean | string;
}

// ========================================
// 검색 및 필터링 타입
// ========================================

export interface ProjectFilters {
  search?: string;
  status?: ProjectStatus[];
  owner?: number[];
  dateRange?: {
    start: string;
    end: string;
  };
  tags?: string[];
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

export interface SortConfig {
  key: string;
  direction: 'asc' | 'desc';
}

// ========================================
// 테마 및 설정 타입
// ========================================

export interface ThemeConfig {
  mode: 'light' | 'dark' | 'system';
  primaryColor: string;
  accentColor: string;
}

export interface UserPreferences {
  theme: ThemeConfig;
  language: 'ko' | 'en';
  notifications: {
    email: boolean;
    push: boolean;
    inApp: boolean;
  };
  privacy: {
    showProfile: boolean;
    showActivity: boolean;
  };
}

// ========================================
// 네트워크 및 상태 타입
// ========================================

export interface LoadingState {
  isLoading: boolean;
  loadingText?: string;
}

export interface ErrorState {
  hasError: boolean;
  error?: Error | APIError;
  errorBoundary?: boolean;
}

export interface NetworkState {
  isOnline: boolean;
  isSlowConnection: boolean;
}

// ========================================
// 이벤트 및 액션 타입
// ========================================

export interface BaseAction {
  type: string;
  payload?: any;
  meta?: any;
}

export interface AsyncAction<T = any> extends BaseAction {
  loading: boolean;
  error?: string;
  data?: T;
}

// ========================================
// 유틸리티 타입
// ========================================

export type Without<T, U> = { [P in Exclude<keyof T, keyof U>]?: never };
export type XOR<T, U> = (T | U) extends object ? (Without<T, U> & U) | (Without<U, T> & T) : T | U;
export type OneOf<T extends readonly unknown[]> = T extends readonly [infer Only] ? Only : T extends readonly [infer A, infer B, ...infer Rest] ? XOR<A, OneOf<[B, ...Rest]>> : never;

export type DeepPartial<T> = T extends object ? {
  [P in keyof T]?: DeepPartial<T[P]>;
} : T;

export type RequiredBy<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type OptionalBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ========================================
// 컴포넌트 props 타입
// ========================================

export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  id?: string;
  'data-testid'?: string;
}

export interface ClickableProps {
  onClick?: (event: React.MouseEvent) => void;
  onDoubleClick?: (event: React.MouseEvent) => void;
  disabled?: boolean;
}

export interface FocusableProps {
  onFocus?: (event: React.FocusEvent) => void;
  onBlur?: (event: React.FocusEvent) => void;
  tabIndex?: number;
  autoFocus?: boolean;
}

// ========================================
// 라우팅 관련 타입
// ========================================

export interface RouteParams {
  [key: string]: string | string[] | undefined;
}

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
  icon?: React.ComponentType<any>;
  badge?: string | number;
  children?: NavigationItem[];
  requireAuth?: boolean;
  roles?: string[];
}

// ========================================
// 영상 피드백 시스템 타입 Re-export
// ========================================

export * from './video-feedback';