/**
 * 애플리케이션에서 사용하는 모든 메시지 상수
 * 하드코딩된 문자열을 방지하고 일관성을 유지하기 위함
 */

// ========================================
// 인증 관련 메시지
// ========================================

export const AUTH_MESSAGES = {
  // 일반 메시지
  LOGIN_SUCCESS: '로그인되었습니다.',
  LOGOUT_SUCCESS: '로그아웃되었습니다.',
  SIGNUP_SUCCESS: '회원가입이 완료되었습니다.',
  
  // 에러 메시지
  LOGIN_FAILED: '로그인에 실패했습니다.',
  SIGNUP_FAILED: '회원가입에 실패했습니다.',
  INVALID_CREDENTIALS: '이메일 또는 비밀번호가 올바르지 않습니다.',
  EMAIL_ALREADY_EXISTS: '이미 사용 중인 이메일입니다.',
  NICKNAME_ALREADY_EXISTS: '이미 사용 중인 닉네임입니다.',
  WEAK_PASSWORD: '비밀번호가 너무 약합니다.',
  PASSWORD_MISMATCH: '비밀번호가 일치하지 않습니다.',
  
  // 소셜 로그인
  GOOGLE_LOGIN_PREPARING: 'Google 로그인 기능은 준비중입니다. 곧 서비스를 제공할 예정입니다.',
  KAKAO_LOGIN_PREPARING: 'Kakao 로그인 기능은 준비중입니다. 곧 서비스를 제공할 예정입니다.',
  GOOGLE_LOGIN_FAILED: 'Google 로그인에 실패했습니다.',
  KAKAO_LOGIN_FAILED: 'Kakao 로그인에 실패했습니다.',
  
  // 비밀번호 재설정
  PASSWORD_RESET_EMAIL_SENT: '비밀번호 재설정 이메일을 발송했습니다.',
  PASSWORD_RESET_SUCCESS: '비밀번호가 성공적으로 재설정되었습니다.',
  PASSWORD_RESET_FAILED: '비밀번호 재설정에 실패했습니다.',
  INVALID_RESET_TOKEN: '유효하지 않은 재설정 토큰입니다.',
  
  // 프로필 관리
  PROFILE_UPDATE_SUCCESS: '프로필이 업데이트되었습니다.',
  PROFILE_UPDATE_FAILED: '프로필 업데이트에 실패했습니다.',
  CURRENT_PASSWORD_INCORRECT: '현재 비밀번호가 올바르지 않습니다.',
  PASSWORD_CHANGE_SUCCESS: '비밀번호가 변경되었습니다.',
  PASSWORD_CHANGE_FAILED: '비밀번호 변경에 실패했습니다.',
} as const;

// ========================================
// 폼 검증 메시지
// ========================================

export const VALIDATION_MESSAGES = {
  // 공통
  REQUIRED_FIELD: '필수 입력 항목입니다.',
  INVALID_FORMAT: '올바른 형식이 아닙니다.',
  
  // 이메일
  EMAIL_REQUIRED: '이메일을 입력해주세요.',
  INVALID_EMAIL_FORMAT: '올바른 이메일 형식이 아닙니다.',
  EMAIL_TOO_LONG: '이메일이 너무 깁니다.',
  
  // 비밀번호
  PASSWORD_REQUIRED: '비밀번호를 입력해주세요.',
  PASSWORD_TOO_SHORT: '비밀번호는 최소 8자 이상이어야 합니다.',
  PASSWORD_TOO_LONG: '비밀번호는 최대 128자까지 가능합니다.',
  PASSWORD_UPPERCASE_REQUIRED: '대문자를 최소 1개 포함해야 합니다.',
  PASSWORD_LOWERCASE_REQUIRED: '소문자를 최소 1개 포함해야 합니다.',
  PASSWORD_NUMBER_REQUIRED: '숫자를 최소 1개 포함해야 합니다.',
  PASSWORD_SPECIAL_CHAR_REQUIRED: '특수문자를 최소 1개 포함해야 합니다.',
  PASSWORD_CONFIRM_REQUIRED: '비밀번호 확인을 입력해주세요.',
  PASSWORD_CONFIRM_MISMATCH: '비밀번호가 일치하지 않습니다.',
  
  // 닉네임
  NICKNAME_REQUIRED: '닉네임을 입력해주세요.',
  NICKNAME_TOO_SHORT: '닉네임은 최소 2자 이상이어야 합니다.',
  NICKNAME_TOO_LONG: '닉네임은 최대 20자까지 가능합니다.',
  NICKNAME_INVALID_CHARS: '한글, 영문, 숫자, _, -만 사용 가능합니다.',
  NICKNAME_FORBIDDEN: '사용할 수 없는 닉네임입니다.',
  
  // 휴대폰
  PHONE_INVALID_FORMAT: '올바른 휴대폰 번호 형식으로 입력해주세요 (예: 010-0000-0000)',
  
  // 회사명
  COMPANY_TOO_LONG: '회사명은 최대 100자까지 가능합니다.',
  
  // 약관 동의
  TERMS_AGREEMENT_REQUIRED: '이용약관에 동의해야 합니다.',
  PRIVACY_AGREEMENT_REQUIRED: '개인정보처리방침에 동의해야 합니다.',
  REQUIRED_AGREEMENTS: '필수 약관에 동의해주세요.',
  
  // 한국어 이름
  KOREAN_NAME_INVALID: '한글 2-10자로 입력해주세요.',
} as const;

// ========================================
// 프로젝트 관련 메시지
// ========================================

export const PROJECT_MESSAGES = {
  // 성공 메시지
  PROJECT_CREATED: '프로젝트가 생성되었습니다.',
  PROJECT_UPDATED: '프로젝트가 업데이트되었습니다.',
  PROJECT_DELETED: '프로젝트가 삭제되었습니다.',
  
  // 에러 메시지
  PROJECT_CREATE_FAILED: '프로젝트 생성에 실패했습니다.',
  PROJECT_UPDATE_FAILED: '프로젝트 업데이트에 실패했습니다.',
  PROJECT_DELETE_FAILED: '프로젝트 삭제에 실패했습니다.',
  PROJECT_NOT_FOUND: '프로젝트를 찾을 수 없습니다.',
  PROJECT_ACCESS_DENIED: '프로젝트에 대한 접근 권한이 없습니다.',
  
  // 검증 메시지
  PROJECT_TITLE_REQUIRED: '프로젝트 제목을 입력해주세요.',
  PROJECT_TITLE_TOO_LONG: '제목은 최대 200자까지 가능합니다.',
  PROJECT_DESCRIPTION_REQUIRED: '프로젝트 설명을 입력해주세요.',
  PROJECT_DESCRIPTION_TOO_LONG: '설명은 최대 1000자까지 가능합니다.',
  PROJECT_START_DATE_INVALID: '날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).',
  PROJECT_START_DATE_PAST: '시작일은 오늘 이후여야 합니다.',
  PROJECT_END_DATE_BEFORE_START: '종료일은 시작일보다 늦어야 합니다.',
  PROJECT_TAGS_TOO_MANY: '태그는 최대 10개까지 추가 가능합니다.',
  PROJECT_TAG_TOO_LONG: '태그는 최대 20자까지 가능합니다.',
} as const;

// ========================================
// 피드백 관련 메시지
// ========================================

export const FEEDBACK_MESSAGES = {
  // 성공 메시지
  FEEDBACK_CREATED: '피드백이 등록되었습니다.',
  FEEDBACK_UPDATED: '피드백이 수정되었습니다.',
  FEEDBACK_DELETED: '피드백이 삭제되었습니다.',
  
  // 에러 메시지
  FEEDBACK_CREATE_FAILED: '피드백 등록에 실패했습니다.',
  FEEDBACK_UPDATE_FAILED: '피드백 수정에 실패했습니다.',
  FEEDBACK_DELETE_FAILED: '피드백 삭제에 실패했습니다.',
  FEEDBACK_NOT_FOUND: '피드백을 찾을 수 없습니다.',
  
  // 검증 메시지
  FEEDBACK_CONTENT_REQUIRED: '피드백 내용을 입력해주세요.',
  FEEDBACK_CONTENT_TOO_LONG: '피드백은 최대 2000자까지 가능합니다.',
  FEEDBACK_TIMESTAMP_INVALID: '유효하지 않은 타임스탬프입니다.',
  FEEDBACK_PROJECT_ID_INVALID: '유효하지 않은 프로젝트 ID입니다.',
} as const;

// ========================================
// 일반 시스템 메시지
// ========================================

export const SYSTEM_MESSAGES = {
  // 로딩
  LOADING: '로딩 중...',
  SAVING: '저장 중...',
  CONNECTING: '연결 중...',
  PROCESSING: '처리 중...',
  
  // 에러
  UNKNOWN_ERROR: '알 수 없는 오류가 발생했습니다.',
  NETWORK_ERROR: '네트워크 오류가 발생했습니다.',
  SERVER_ERROR: '서버 오류가 발생했습니다.',
  PERMISSION_DENIED: '권한이 없습니다.',
  SERVICE_UNAVAILABLE: '서비스를 일시적으로 사용할 수 없습니다.',
  
  // 확인/취소
  CONFIRM: '확인',
  CANCEL: '취소',
  SAVE: '저장',
  DELETE: '삭제',
  EDIT: '수정',
  CREATE: '생성',
  
  // 상태
  SUCCESS: '성공',
  WARNING: '경고',
  ERROR: '오류',
  INFO: '정보',
  
  // 데이터 없음
  NO_DATA: '데이터가 없습니다.',
  NO_RESULTS: '검색 결과가 없습니다.',
  EMPTY_LIST: '목록이 비어있습니다.',
  
  // 준비중
  COMING_SOON: '곧 서비스를 제공할 예정입니다.',
  PREPARING: '준비중',
  UNDER_DEVELOPMENT: '개발 중',
} as const;

// ========================================
// UI 텍스트
// ========================================

export const UI_TEXT = {
  // 네비게이션
  DASHBOARD: '대시보드',
  PROJECTS: '프로젝트',
  FEEDBACK: '피드백',
  CALENDAR: '일정',
  MYPAGE: '마이페이지',
  
  // 버튼
  LOGIN: '로그인',
  SIGNUP: '회원가입',
  LOGOUT: '로그아웃',
  NEXT: '다음',
  PREVIOUS: '이전',
  SUBMIT: '제출',
  RESET: '재설정',
  
  // 폼 라벨
  EMAIL: '이메일',
  PASSWORD: '비밀번호',
  PASSWORD_CONFIRM: '비밀번호 확인',
  NICKNAME: '닉네임',
  PHONE: '연락처',
  COMPANY: '회사명',
  
  // 상태 표시
  REQUIRED: '*',
  OPTIONAL: '(선택)',
  RECOMMENDED: '(권장)',
  
  // 플레이스홀더
  EMAIL_PLACEHOLDER: 'name@company.com',
  PASSWORD_PLACEHOLDER: '8자 이상, 대소문자, 숫자, 특수문자 포함',
  PHONE_PLACEHOLDER: '010-0000-0000',
  COMPANY_PLACEHOLDER: '회사명을 입력해주세요',
  NICKNAME_PLACEHOLDER: '사용하실 닉네임을 입력해주세요',
} as const;

// ========================================
// 유틸리티 타입
// ========================================

export type AuthMessage = keyof typeof AUTH_MESSAGES;
export type ValidationMessage = keyof typeof VALIDATION_MESSAGES;
export type ProjectMessage = keyof typeof PROJECT_MESSAGES;
export type FeedbackMessage = keyof typeof FEEDBACK_MESSAGES;
export type SystemMessage = keyof typeof SYSTEM_MESSAGES;
export type UIText = keyof typeof UI_TEXT;

// ========================================
// 헬퍼 함수
// ========================================

/**
 * 메시지 객체에서 값을 안전하게 가져오는 헬퍼 함수
 */
export function getMessage<T extends Record<string, string>>(
  messageObj: T,
  key: keyof T,
  fallback?: string
): string {
  return messageObj[key] || fallback || '메시지를 찾을 수 없습니다.';
}

/**
 * 동적 메시지 생성 헬퍼 함수
 */
export function createMessage(template: string, variables: Record<string, string | number>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return variables[key]?.toString() || match;
  });
}