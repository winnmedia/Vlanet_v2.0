import { z } from 'zod';
import { VALIDATION_MESSAGES } from '@/utils/constants/messages';

// ========================================
// 기본 스키마 정의
// ========================================

/**
 * 한국어 이름 스키마
 */
export const koreanNameSchema = z.string().regex(
  /^[가-힣]{2,10}$/,
  VALIDATION_MESSAGES.KOREAN_NAME_INVALID
);

/**
 * 전화번호 스키마
 * 010, 011, 016, 017, 018, 019 시작 번호만 허용
 */
export const phoneNumberSchema = z.string().regex(
  /^(010|011|016|017|018|019)-\d{4}-\d{4}$/,
  VALIDATION_MESSAGES.PHONE_INVALID_FORMAT
);

/**
 * 강력한 비밀번호 스키마
 */
export const strongPasswordSchema = z.string()
  .min(8, VALIDATION_MESSAGES.PASSWORD_TOO_SHORT)
  .max(128, VALIDATION_MESSAGES.PASSWORD_TOO_LONG)
  .regex(/[A-Z]/, VALIDATION_MESSAGES.PASSWORD_UPPERCASE_REQUIRED)
  .regex(/[a-z]/, VALIDATION_MESSAGES.PASSWORD_LOWERCASE_REQUIRED)
  .regex(/[0-9]/, VALIDATION_MESSAGES.PASSWORD_NUMBER_REQUIRED)
  .regex(/[!@#$%^&*(),.?":{}|<>]/, VALIDATION_MESSAGES.PASSWORD_SPECIAL_CHAR_REQUIRED);

/**
 * 닉네임 스키마
 */
export const nicknameSchema = z.string()
  .min(2, VALIDATION_MESSAGES.NICKNAME_TOO_SHORT)
  .max(20, VALIDATION_MESSAGES.NICKNAME_TOO_LONG)
  .regex(/^[가-힣a-zA-Z0-9_-]+$/, VALIDATION_MESSAGES.NICKNAME_INVALID_CHARS)
  .refine(
    (value) => !['admin', 'administrator', '', 'root', 'system'].includes(value.toLowerCase()),
    VALIDATION_MESSAGES.NICKNAME_FORBIDDEN
  );

// ========================================
// 인증 관련 스키마
// ========================================

/**
 * 로그인 스키마
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
 *   
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
  phone: z.string().optional(),
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
 *    
 */
export const passwordResetRequestSchema = z.object({
  email: z.string()
    .min(1, VALIDATION_MESSAGES.EMAIL_REQUIRED)
    .email(VALIDATION_MESSAGES.INVALID_EMAIL_FORMAT),
});

/**
 *   
 */
export const passwordResetSchema = z.object({
  token: z.string().min(1, '토큰이 필요합니다'),
  password: strongPasswordSchema,
  passwordConfirm: z.string()
    .min(1, VALIDATION_MESSAGES.PASSWORD_CONFIRM_REQUIRED),
}).refine(
  (data) => data.password === data.passwordConfirm,
  {
    message: VALIDATION_MESSAGES.PASSWORD_CONFIRM_MISMATCH,
    path: ['passwordConfirm'],
  }
);

/**
 *    
 */
export const emailCheckSchema = z.object({
  email: z.string()
    .min(1, VALIDATION_MESSAGES.EMAIL_REQUIRED)
    .email(VALIDATION_MESSAGES.INVALID_EMAIL_FORMAT),
});

/**
 *    
 */
export const nicknameCheckSchema = z.object({
  nickname: nicknameSchema,
});

/**
 *   
 */
export const profileUpdateSchema = z.object({
  nickname: nicknameSchema.optional(),
  phone: phoneNumberSchema.optional(),
  company: z.string()
    .max(100, '  100 ')
    .optional(),
  profile_image: z.string().url(' URL  ').optional(),
});

/**
 *   
 */
export const passwordChangeSchema = z.object({
  currentPassword: z.string()
    .min(1, '  '),
  newPassword: strongPasswordSchema,
  newPasswordConfirm: z.string()
    .min(1, '   '),
}).refine(
  (data) => data.newPassword === data.newPasswordConfirm,
  {
    message: '   ',
    path: ['newPasswordConfirm'],
  }
).refine(
  (data) => data.currentPassword !== data.newPassword,
  {
    message: '    ',
    path: ['newPassword'],
  }
);

// ========================================
//   
// ========================================

/**
 *   
 */
export const createProjectSchema = z.object({
  title: z.string()
    .min(1, '  ')
    .max(200, '  200 ')
    .trim(),
  description: z.string()
    .min(1, '  ')
    .max(1000, '  1000 ')
    .trim(),
  start_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '    (YYYY-MM-DD)')
    .refine(
      (date) => new Date(date) >= new Date(new Date().toDateString()),
      '   '
    ),
  end_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '    (YYYY-MM-DD)'),
  status: z.enum(['planning', 'production', 'review', 'completed', 'archived'])
    .default('planning'),
  is_public: z.boolean().default(false),
  tags: z.array(z.string().max(20, '  20 '))
    .max(10, '  10  ')
    .optional(),
}).refine(
  (data) => new Date(data.end_date) > new Date(data.start_date),
  {
    message: '   ',
    path: ['end_date'],
  }
);

/**
 *   
 */
export const updateProjectSchema = z.object({
  title: z.string()
    .min(1, '  ')
    .max(200, '  200 ')
    .trim()
    .optional(),
  description: z.string()
    .min(1, '  ')
    .max(1000, '  1000 ')
    .trim()
    .optional(),
  start_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '    (YYYY-MM-DD)')
    .optional(),
  end_date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '    (YYYY-MM-DD)')
    .optional(),
  status: z.enum(['planning', 'production', 'review', 'completed', 'archived'])
    .optional(),
  is_public: z.boolean().optional(),
  tags: z.array(z.string().max(20, '  20 '))
    .max(10, '  10  ')
    .optional(),
});

/**
 *    
 */
export const projectFiltersSchema = z.object({
  search: z.string().max(100, '  100 ').optional(),
  status: z.array(z.enum(['planning', 'production', 'review', 'completed', 'archived']))
    .optional(),
  owner: z.array(z.number().positive('   ID')).optional(),
  dateRange: z.object({
    start: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '   '),
    end: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, '   '),
  }).refine(
    (data) => new Date(data.end) >= new Date(data.start),
    {
      message: '    ',
      path: ['end'],
    }
  ).optional(),
  tags: z.array(z.string().max(20, '  20 ')).optional(),
});

// ========================================
//   
// ========================================

/**
 *   
 */
export const createFeedbackSchema = z.object({
  content: z.string()
    .min(1, '  ')
    .max(2000, '  2000 ')
    .trim(),
  timestamp: z.number()
    .min(0, '  ')
    .optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical'])
    .default('medium'),
  project_id: z.number().positive('   ID'),
});

/**
 *   
 */
export const updateFeedbackSchema = z.object({
  content: z.string()
    .min(1, '  ')
    .max(2000, '  2000 ')
    .trim()
    .optional(),
  status: z.enum(['pending', 'in-progress', 'resolved', 'rejected']).optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical']).optional(),
});

// ========================================
//  
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
//  
// ========================================

/**
 *    
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
 *   
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
 *      
 */
export function getFirstError(errors: z.ZodError, field: string): string | undefined {
  const issue = errors.issues.find(
    (issue) => issue.path.join('.') === field
  );
  return issue?.message;
}