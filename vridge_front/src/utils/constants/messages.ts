/**
 *     
 *      
 */

// ========================================
//   
// ========================================

export const AUTH_MESSAGES = {
  //  
  LOGIN_SUCCESS: '.',
  LOGOUT_SUCCESS: '.',
  SIGNUP_SUCCESS: ' .',
  
  //  
  LOGIN_FAILED: ' .',
  SIGNUP_FAILED: ' .',
  INVALID_CREDENTIALS: '    .',
  EMAIL_ALREADY_EXISTS: '   .',
  NICKNAME_ALREADY_EXISTS: '   .',
  WEAK_PASSWORD: '  .',
  PASSWORD_MISMATCH: '  .',
  
  //  
  GOOGLE_LOGIN_PREPARING: 'Google   .    .',
  KAKAO_LOGIN_PREPARING: 'Kakao   .    .',
  GOOGLE_LOGIN_FAILED: 'Google  .',
  KAKAO_LOGIN_FAILED: 'Kakao  .',
  
  //  
  PASSWORD_RESET_EMAIL_SENT: '   .',
  PASSWORD_RESET_SUCCESS: '  .',
  PASSWORD_RESET_FAILED: '  .',
  INVALID_RESET_TOKEN: '   .',
  
  //  
  PROFILE_UPDATE_SUCCESS: ' .',
  PROFILE_UPDATE_FAILED: '  .',
  CURRENT_PASSWORD_INCORRECT: '   .',
  PASSWORD_CHANGE_SUCCESS: ' .',
  PASSWORD_CHANGE_FAILED: '  .',
} as const;

// ========================================
//   
// ========================================

export const VALIDATION_MESSAGES = {
  // 
  REQUIRED_FIELD: '  .',
  INVALID_FORMAT: '  .',
  
  // 
  EMAIL_REQUIRED: ' .',
  INVALID_EMAIL_FORMAT: '   .',
  EMAIL_TOO_LONG: '  .',
  
  // 
  PASSWORD_REQUIRED: ' .',
  PASSWORD_TOO_SHORT: '  8  .',
  PASSWORD_TOO_LONG: '  128 .',
  PASSWORD_UPPERCASE_REQUIRED: '  1  .',
  PASSWORD_LOWERCASE_REQUIRED: '  1  .',
  PASSWORD_NUMBER_REQUIRED: '  1  .',
  PASSWORD_SPECIAL_CHAR_REQUIRED: '  1  .',
  PASSWORD_CONFIRM_REQUIRED: '  .',
  PASSWORD_CONFIRM_MISMATCH: '  .',
  
  // 
  NICKNAME_REQUIRED: ' .',
  NICKNAME_TOO_SHORT: '  2  .',
  NICKNAME_TOO_LONG: '  20 .',
  NICKNAME_INVALID_CHARS: ', , , _, -  .',
  NICKNAME_FORBIDDEN: '   .',
  
  // 
  PHONE_INVALID_FORMAT: '     (: 010-0000-0000)',
  
  // 
  COMPANY_TOO_LONG: '  100 .',
  
  //  
  TERMS_AGREEMENT_REQUIRED: '  .',
  PRIVACY_AGREEMENT_REQUIRED: '  .',
  REQUIRED_AGREEMENTS: '  .',
  
  //  
  KOREAN_NAME_INVALID: ' 2-10 .',
} as const;

// ========================================
//   
// ========================================

export const PROJECT_MESSAGES = {
  //  
  PROJECT_CREATED: ' .',
  PROJECT_UPDATED: ' .',
  PROJECT_DELETED: ' .',
  
  //  
  PROJECT_CREATE_FAILED: '  .',
  PROJECT_UPDATE_FAILED: '  .',
  PROJECT_DELETE_FAILED: '  .',
  PROJECT_NOT_FOUND: '   .',
  PROJECT_ACCESS_DENIED: '    .',
  
  //  
  PROJECT_TITLE_REQUIRED: '  .',
  PROJECT_TITLE_TOO_LONG: '  200 .',
  PROJECT_DESCRIPTION_REQUIRED: '  .',
  PROJECT_DESCRIPTION_TOO_LONG: '  1000 .',
  PROJECT_START_DATE_INVALID: '    (YYYY-MM-DD).',
  PROJECT_START_DATE_PAST: '   .',
  PROJECT_END_DATE_BEFORE_START: '   .',
  PROJECT_TAGS_TOO_MANY: '  10  .',
  PROJECT_TAG_TOO_LONG: '  20 .',
} as const;

// ========================================
//   
// ========================================

export const FEEDBACK_MESSAGES = {
  //  
  FEEDBACK_CREATED: ' .',
  FEEDBACK_UPDATED: ' .',
  FEEDBACK_DELETED: ' .',
  
  //  
  FEEDBACK_CREATE_FAILED: '  .',
  FEEDBACK_UPDATE_FAILED: '  .',
  FEEDBACK_DELETE_FAILED: '  .',
  FEEDBACK_NOT_FOUND: '   .',
  
  //  
  FEEDBACK_CONTENT_REQUIRED: '  .',
  FEEDBACK_CONTENT_TOO_LONG: '  2000 .',
  FEEDBACK_TIMESTAMP_INVALID: '  .',
  FEEDBACK_PROJECT_ID_INVALID: '   ID.',
} as const;

// ========================================
//   
// ========================================

export const SYSTEM_MESSAGES = {
  // 
  LOADING: ' ...',
  SAVING: ' ...',
  CONNECTING: ' ...',
  PROCESSING: ' ...',
  
  // 
  UNKNOWN_ERROR: '    .',
  NETWORK_ERROR: '  .',
  SERVER_ERROR: '  .',
  PERMISSION_DENIED: ' .',
  SERVICE_UNAVAILABLE: '    .',
  
  // /
  CONFIRM: '',
  CANCEL: '',
  SAVE: '',
  DELETE: '',
  EDIT: '',
  CREATE: '',
  
  // 
  SUCCESS: '',
  WARNING: '',
  ERROR: '',
  INFO: '',
  
  //  
  NO_DATA: ' .',
  NO_RESULTS: '  .',
  EMPTY_LIST: ' .',
  
  // 
  COMING_SOON: '   .',
  PREPARING: '',
  UNDER_DEVELOPMENT: ' ',
} as const;

// ========================================
// UI 
// ========================================

export const UI_TEXT = {
  // 
  DASHBOARD: '',
  PROJECTS: '',
  FEEDBACK: '',
  CALENDAR: '',
  MYPAGE: '',
  
  // 
  LOGIN: '',
  SIGNUP: '',
  LOGOUT: '',
  NEXT: '',
  PREVIOUS: '',
  SUBMIT: '',
  RESET: '',
  
  //  
  EMAIL: '',
  PASSWORD: '',
  PASSWORD_CONFIRM: ' ',
  NICKNAME: '',
  PHONE: '',
  COMPANY: '',
  
  //  
  REQUIRED: '*',
  OPTIONAL: '()',
  RECOMMENDED: '()',
  
  // 
  EMAIL_PLACEHOLDER: 'name@company.com',
  PASSWORD_PLACEHOLDER: '8 , , ,  ',
  PHONE_PLACEHOLDER: '010-0000-0000',
  COMPANY_PLACEHOLDER: ' ',
  NICKNAME_PLACEHOLDER: '  ',
} as const;

// ========================================
//  
// ========================================

export type AuthMessage = keyof typeof AUTH_MESSAGES;
export type ValidationMessage = keyof typeof VALIDATION_MESSAGES;
export type ProjectMessage = keyof typeof PROJECT_MESSAGES;
export type FeedbackMessage = keyof typeof FEEDBACK_MESSAGES;
export type SystemMessage = keyof typeof SYSTEM_MESSAGES;
export type UIText = keyof typeof UI_TEXT;

// ========================================
//  
// ========================================

/**
 *       
 */
export function getMessage<T extends Record<string, string>>(
  messageObj: T,
  key: keyof T,
  fallback?: string
): string {
  return messageObj[key] || fallback || '   .';
}

/**
 *     
 */
export function createMessage(template: string, variables: Record<string, string | number>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return variables[key]?.toString() || match;
  });
}