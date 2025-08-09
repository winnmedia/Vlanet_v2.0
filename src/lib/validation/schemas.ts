import { z } from 'zod';
import { VALIDATION_MESSAGES } from '@/utils/constants/messages';

// ========================================
// 기본 유틸리티 스키마
// ========================================

/**
 * 한국어 이름 형식 검증
 */
export const koreanNameSchema = z.string().regex(
  /^[가-힣]{2,10}$/,
  VALIDATION_MESSAGES.KOREAN_NAME_INVALID
);

/**
 * 한국 휴대폰 번호 형식 검증
 * 010, 011, 016, 017, 018, 019 번호 지원
 */
export const phoneNumberSchema = z.string().regex(
  /^(010|011|016|017|018|019)-\d{4}-\d{4}$/,
  VALIDATION_MESSAGES.PHONE_INVALID_FORMAT
);

/**
 * 강력한 비밀번호 검증
 */
export const strongPasswordSchema = z.string()
  .min(8, VALIDATION_MESSAGES.PASSWORD_TOO_SHORT)
  .max(128, VALIDATION_MESSAGES.PASSWORD_TOO_LONG)
  .regex(/[A-Z]/, VALIDATION_MESSAGES.PASSWORD_UPPERCASE_REQUIRED)
  .regex(/[a-z]/, VALIDATION_MESSAGES.PASSWORD_LOWERCASE_REQUIRED)
  .regex(/[0-9]/, VALIDATION_MESSAGES.PASSWORD_NUMBER_REQUIRED)
  .regex(/[!@#$%^&*(),.?":{}|<>]/, VALIDATION_MESSAGES.PASSWORD_SPECIAL_CHAR_REQUIRED);

/**
 * 닉네임 형식 검증
 */
export const nicknameSchema = z.string()
  .min(2, VALIDATION_MESSAGES.NICKNAME_TOO_SHORT)
  .max(20, VALIDATION_MESSAGES.NICKNAME_TOO_LONG)
  .regex(/^[가-힣a-zA-Z0-9_-]+$/, VALIDATION_MESSAGES.NICKNAME_INVALID_CHARS)
  .refine(
    (value) => !['admin', 'administrator', '관리자', 'root', 'system'].includes(value.toLowerCase()),
    VALIDATION_MESSAGES.NICKNAME_FORBIDDEN
  );

// ========================================
// 인증 관련 스키마
// ========================================

/**
 * 로그인 요청 스키마
 */
export const loginSchema = z.object({
  email: z.string()
    .min(1, VALIDATION_MESSAGES.EMAIL_REQUIRED)
    .email(VALIDATION_MESSAGES.INVALID_EMAIL_FORMAT)
    .max(254, VALIDATION_MESSAGES.EMAIL_TOO_LONG),
  password: z.string()
    .min(1, VALIDATION_MESSAGES.PASSWORD_REQUIRED)
    .min(8, VALIDATION_MESSAGES.PASSWORD_TOO_SHORT),
  rememberMe: z.boolean().optional().default(false),
});

/**
 * 회원가입 요청 스키마
 */
export const signupSchema = z.object({
  email: z.string()
    .min(1, VALIDATION_MESSAGES.EMAIL_REQUIRED)
    .email(VALIDATION_MESSAGES.INVALID_EMAIL_FORMAT)
    .max(254, VALIDATION_MESSAGES.EMAIL_TOO_LONG),
  password: strongPasswordSchema,
  passwordConfirm: z.string()
    .min(1, VALIDATION_MESSAGES.PASSWORD_CONFIRM_REQUIRED),
  nickname: nicknameSchema,
  phone: phoneNumberSchema.optional(),
  company: z.string()
    .max(100, VALIDATION_MESSAGES.COMPANY_TOO_LONG)
    .optional(),
  agreedToTerms: z.boolean()
    .refine(val => val === true, VALIDATION_MESSAGES.TERMS_AGREEMENT_REQUIRED),
  agreedToPrivacy: z.boolean()
    .refine(val => val === true, VALIDATION_MESSAGES.PRIVACY_AGREEMENT_REQUIRED),
  agreedToMarketing: z.boolean().optional().default(false),
}).refine(
  (data) => data.password === data.passwordConfirm,
  {
    message: VALIDATION_MESSAGES.PASSWORD_CONFIRM_MISMATCH,
    path: ['passwordConfirm'],
  }
);

/**
 * 비밀번호 재설정 요청 스키마
 */
export const passwordResetRequestSchema = z.object({
  email: z.string()
    .min(1, '이메일을 입력해주세요')
    .email('올바른 이메일 형식이 아닙니다'),
});

/**
 * 비밀번호 재설정 스키마
 */
export const passwordResetSchema = z.object({
  token: z.string().min(1, '유효하지 않은 토큰입니다'),
  password: strongPasswordSchema,
  passwordConfirm: z.string()
    .min(1, '비밀번호 확인을 입력해주세요'),
}).refine(
  (data) => data.password === data.passwordConfirm,
  {
    message: '비밀번호가 일치하지 않습니다',
    path: ['passwordConfirm'],
  }
);

/**
 * 이메일 중복 확인 스키마
 */
export const emailCheckSchema = z.object({
  email: z.string()
    .min(1, '이메일을 입력해주세요')
    .email('올바른 이메일 형식이 아닙니다'),
});

/**
 * 닉네임 중복 확인 스키마
 */
export const nicknameCheckSchema = z.object({
  nickname: nicknameSchema,
});

/**
 * 프로필 업데이트 스키마
 */
export const profileUpdateSchema = z.object({
  nickname: nicknameSchema.optional(),
  phone: phoneNumberSchema.optional(),
  company: z.string()
    .max(100, '회사명은 최대 100자까지 가능합니다')
    .optional(),
  profile_image: z.string().url('올바른 URL 형식이 아닙니다').optional(),
});

/**
 * 비밀번호 변경 스키마
 */
export const passwordChangeSchema = z.object({
  currentPassword: z.string()
    .min(1, '현재 비밀번호를 입력해주세요'),
  newPassword: strongPasswordSchema,
  newPasswordConfirm: z.string()
    .min(1, '새 비밀번호 확인을 입력해주세요'),
}).refine(
  (data) => data.newPassword === data.newPasswordConfirm,
  {
    message: '새 비밀번호가 일치하지 않습니다',
    path: ['newPasswordConfirm'],
  }
).refine(
  (data) => data.currentPassword !== data.newPassword,
  {
    message: '현재 비밀번호와 새 비밀번호가 같습니다',
    path: ['newPassword'],
  }
);

// ========================================
// 프로젝트 관련 스키마
// ========================================

/**
 * 프로젝트 생성 스키마
 */
export const createProjectSchema = z.object({
  title: z.string()
    .min(1, '프로젝트 제목을 입력해주세요')
    .max(200, '제목은 최대 200자까지 가능합니다')
    .trim(),
  description: z.string()
    .min(1, '프로젝트 설명을 입력해주세요')
    .max(1000, '설명은 최대 1000자까지 가능합니다')
    .trim(),
  start_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)')
    .refine(
      (date) => new Date(date) >= new Date(new Date().toDateString()),
      '시작일은 오늘 이후여야 합니다'
    ),
  end_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)'),
  status: z.enum(['planning', 'production', 'review', 'completed', 'archived'])
    .default('planning'),
  is_public: z.boolean().default(false),
  tags: z.array(z.string().max(20, '태그는 최대 20자까지 가능합니다'))
    .max(10, '태그는 최대 10개까지 추가 가능합니다')
    .optional(),
}).refine(
  (data) => new Date(data.end_date) > new Date(data.start_date),
  {
    message: '종료일은 시작일보다 늦어야 합니다',
    path: ['end_date'],
  }
);

/**
 * 프로젝트 업데이트 스키마
 */
export const updateProjectSchema = z.object({
  title: z.string()
    .min(1, '프로젝트 제목을 입력해주세요')
    .max(200, '제목은 최대 200자까지 가능합니다')
    .trim()
    .optional(),
  description: z.string()
    .min(1, '프로젝트 설명을 입력해주세요')
    .max(1000, '설명은 최대 1000자까지 가능합니다')
    .trim()
    .optional(),
  start_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)')
    .optional(),
  end_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)')
    .optional(),
  status: z.enum(['planning', 'production', 'review', 'completed', 'archived'])
    .optional(),
  is_public: z.boolean().optional(),
  tags: z.array(z.string().max(20, '태그는 최대 20자까지 가능합니다'))
    .max(10, '태그는 최대 10개까지 추가 가능합니다')
    .optional(),
});

/**
 * 프로젝트 검색 필터 스키마
 */
export const projectFiltersSchema = z.object({
  search: z.string().max(100, '검색어는 최대 100자까지 가능합니다').optional(),
  status: z.array(z.enum(['planning', 'production', 'review', 'completed', 'archived']))
    .optional(),
  owner: z.array(z.number().positive('유효하지 않은 사용자 ID입니다')).optional(),
  dateRange: z.object({
    start: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다'),
    end: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '날짜 형식이 올바르지 않습니다'),
  }).refine(
    (data) => new Date(data.end) >= new Date(data.start),
    {
      message: '종료일은 시작일보다 늦거나 같아야 합니다',
      path: ['end'],
    }
  ).optional(),
  tags: z.array(z.string().max(20, '태그는 최대 20자까지 가능합니다')).optional(),
});

// ========================================
// 피드백 관련 스키마
// ========================================

/**
 * 피드백 생성 스키마
 */
export const createFeedbackSchema = z.object({
  content: z.string()
    .min(1, '피드백 내용을 입력해주세요')
    .max(2000, '피드백은 최대 2000자까지 가능합니다')
    .trim(),
  timestamp: z.number()
    .min(0, '유효하지 않은 타임스탬프입니다')
    .optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical'])
    .default('medium'),
  project_id: z.number().positive('유효하지 않은 프로젝트 ID입니다'),
});

/**
 * 피드백 업데이트 스키마
 */
export const updateFeedbackSchema = z.object({
  content: z.string()
    .min(1, '피드백 내용을 입력해주세요')
    .max(2000, '피드백은 최대 2000자까지 가능합니다')
    .trim()
    .optional(),
  status: z.enum(['pending', 'in-progress', 'resolved', 'rejected']).optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical']).optional(),
});

// ========================================
// 타입 추론
// ========================================

export type LoginFormData = z.infer<typeof loginSchema>;
export type SignupFormData = z.infer<typeof signupSchema>;
export type PasswordResetRequestData = z.infer<typeof passwordResetRequestSchema>;
export type PasswordResetData = z.infer<typeof passwordResetSchema>;
export type EmailCheckData = z.infer<typeof emailCheckSchema>;
export type NicknameCheckData = z.infer<typeof nicknameCheckSchema>;
export type ProfileUpdateData = z.infer<typeof profileUpdateSchema>;
export type PasswordChangeData = z.infer<typeof passwordChangeSchema>;
export type CreateProjectData = z.infer<typeof createProjectSchema>;
export type UpdateProjectData = z.infer<typeof updateProjectSchema>;
export type ProjectFiltersData = z.infer<typeof projectFiltersSchema>;
export type CreateFeedbackData = z.infer<typeof createFeedbackSchema>;
export type UpdateFeedbackData = z.infer<typeof updateFeedbackSchema>;

// ========================================
// 유틸리티 함수
// ========================================

/**
 * 스키마 유효성 검사 헬퍼
 */
export function validateSchema<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: z.ZodError } {
  try {
    const result = schema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error };
    }
    throw error;
  }
}

/**
 * 에러 메시지 포맷팅
 */
export function formatValidationErrors(errors: z.ZodError): Record<string, string> {
  const formattedErrors: Record<string, string> = {};
  
  errors.issues.forEach((issue) => {
    const path = issue.path.join('.');
    formattedErrors[path] = issue.message;
  });
  
  return formattedErrors;
}

/**
 * 필드별 첫 번째 에러 메시지만 반환
 */
export function getFirstError(errors: z.ZodError, field: string): string | undefined {
  const issue = errors.issues.find(
    (issue) => issue.path.join('.') === field
  );
  return issue?.message;
}