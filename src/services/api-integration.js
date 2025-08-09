/**
 * VideoPlanet API 통합 서비스
 * Backend URL: https://videoplanet.up.railway.app
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://videoplanet.up.railway.app';

// API 헬퍼 함수
const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('accessToken');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
};

// 1. 프로젝트 API
export const projectAPI = {
  // 프로젝트 목록 조회
  list: () => apiRequest('/api/projects/'),

  // 프로젝트 생성 (수정된 버전)
  create: async (projectData) => {
    // 멱등성 키 생성 (중복 생성 방지)
    const idempotencyKey = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    return apiRequest('/api/projects/create/', {
      method: 'POST',
      headers: {
        'X-Idempotency-Key': idempotencyKey
      },
      body: JSON.stringify({
        name: projectData.name,
        manager: projectData.manager,
        consumer: projectData.consumer,
        description: projectData.description || '',
        color: projectData.color || '#1631F8',
        process: projectData.process || []
      })
    });
  },

  // 프로젝트 상세 조회
  detail: (projectId) => apiRequest(`/api/projects/detail/${projectId}/`),

  // 프로젝트 수정
  update: (projectId, data) => apiRequest(`/api/projects/detail/${projectId}/`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),

  // 프로젝트 삭제
  delete: (projectId) => apiRequest(`/api/projects/detail/${projectId}/`, {
    method: 'DELETE'
  }),

  // 일정 업데이트
  updateSchedule: (projectId, scheduleData) => apiRequest(`/api/projects/date_update/${projectId}`, {
    method: 'POST',
    body: JSON.stringify(scheduleData)
  })
};

// 2. 영상 기획 API
export const planningAPI = {
  // 기획 목록
  list: () => apiRequest('/api/video-planning/list/'),

  // 기획 생성
  create: (planningData) => apiRequest('/api/video-planning/create/', {
    method: 'POST',
    body: JSON.stringify(planningData)
  }),

  // 기획 상세
  detail: (planningId) => apiRequest(`/api/video-planning/detail/${planningId}/`),

  // AI 생성 기능들
  generateStructure: (data) => apiRequest('/api/video-planning/generate/structure/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  generateStory: (data) => apiRequest('/api/video-planning/generate/story/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  generateScenes: (data) => apiRequest('/api/video-planning/generate/scenes/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // 스토리보드 생성
  generateStoryboards: (data) => apiRequest('/api/video-planning/generate/storyboards/', {
    method: 'POST',
    body: JSON.stringify(data)
  })
};

// 3. 피드백 API
export const feedbackAPI = {
  // 프로젝트 피드백 조회
  getProjectFeedback: (projectId) => apiRequest(`/api/projects/${projectId}/feedback/`),

  // 피드백 파일 업로드
  uploadFeedback: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('accessToken');
    
    const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/feedback/upload/`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
  },

  // 피드백 코멘트 작성
  addComment: (projectId, commentData) => apiRequest(`/api/projects/${projectId}/feedback/comments/`, {
    method: 'POST',
    body: JSON.stringify(commentData)
  }),

  // 인코딩 상태 확인
  checkEncodingStatus: (projectId) => apiRequest(`/api/projects/${projectId}/feedback/encoding-status/`)
};

// 4. 에러 핸들링 전략
export const errorHandler = {
  // 에러 타입별 처리
  handle: (error, context) => {
    console.error(`Error in ${context}:`, error);

    // 인증 에러
    if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
      // 토큰 갱신 시도
      return refreshToken();
    }

    // 권한 에러
    if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
      return {
        error: true,
        message: '권한이 없습니다.',
        code: 'FORBIDDEN'
      };
    }

    // 서버 에러
    if (error.message?.includes('500') || error.message?.includes('Internal Server Error')) {
      return {
        error: true,
        message: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
        code: 'SERVER_ERROR'
      };
    }

    // 네트워크 에러
    if (error.message?.includes('NetworkError') || error.message?.includes('fetch')) {
      return {
        error: true,
        message: '네트워크 연결을 확인해주세요.',
        code: 'NETWORK_ERROR'
      };
    }

    // 기본 에러
    return {
      error: true,
      message: error.message || '알 수 없는 오류가 발생했습니다.',
      code: 'UNKNOWN_ERROR'
    };
  },

  // 재시도 로직
  retry: async (fn, retries = 3, delay = 1000) => {
    for (let i = 0; i < retries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (i === retries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }
};

// 토큰 갱신
async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) {
    window.location.href = '/login';
    return;
  }

  try {
    const response = await apiRequest('/api/auth/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken })
    });

    localStorage.setItem('accessToken', response.access);
    return response;
  } catch (error) {
    console.error('Token refresh failed:', error);
    window.location.href = '/login';
  }
}

// 사용 예시
export const examples = {
  // 프로젝트 생성 예시
  createProject: async () => {
    try {
      const projectData = {
        name: '새 프로젝트',
        manager: '홍길동',
        consumer: 'ABC 회사',
        description: '프로젝트 설명',
        process: [
          { key: 'basic_plan', startDate: '2025-01-01', endDate: '2025-01-07' },
          { key: 'story_board', startDate: '2025-01-08', endDate: '2025-01-14' }
        ]
      };

      const result = await projectAPI.create(projectData);
      console.log('프로젝트 생성 성공:', result);
      return result;
    } catch (error) {
      const handled = errorHandler.handle(error, 'createProject');
      console.error('프로젝트 생성 실패:', handled);
      return handled;
    }
  },

  // 피드백 업로드 예시 (재시도 포함)
  uploadFeedbackWithRetry: async (projectId, file) => {
    return errorHandler.retry(
      () => feedbackAPI.uploadFeedback(projectId, file),
      3,  // 3번 재시도
      2000  // 2초 간격
    );
  }
};

export default {
  projectAPI,
  planningAPI,
  feedbackAPI,
  errorHandler,
  examples
};