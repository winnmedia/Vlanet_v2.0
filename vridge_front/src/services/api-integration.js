/**
 * VideoPlanet API  
 * Backend URL: https://videoplanet.up.railway.app
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://videoplanet.up.railway.app';

// API  
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

// 1.  API
export const projectAPI = {
  //   
  list: () => apiRequest('/api/projects/'),

  //   ( )
  create: async (projectData) => {
    //    (  )
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

  //   
  detail: (projectId) => apiRequest(`/api/projects/detail/${projectId}/`),

  //  
  update: (projectId, data) => apiRequest(`/api/projects/detail/${projectId}/`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),

  //  
  delete: (projectId) => apiRequest(`/api/projects/detail/${projectId}/`, {
    method: 'DELETE'
  }),

  //  
  updateSchedule: (projectId, scheduleData) => apiRequest(`/api/projects/date_update/${projectId}`, {
    method: 'POST',
    body: JSON.stringify(scheduleData)
  })
};

// 2.   API
export const planningAPI = {
  //  
  list: () => apiRequest('/api/video-planning/list/'),

  //  
  create: (planningData) => apiRequest('/api/video-planning/create/', {
    method: 'POST',
    body: JSON.stringify(planningData)
  }),

  //  
  detail: (planningId) => apiRequest(`/api/video-planning/detail/${planningId}/`),

  // AI  
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

  //  
  generateStoryboards: (data) => apiRequest('/api/video-planning/generate/storyboards/', {
    method: 'POST',
    body: JSON.stringify(data)
  })
};

// 3.  API
export const feedbackAPI = {
  //   
  getProjectFeedback: (projectId) => apiRequest(`/api/projects/${projectId}/feedback/`),

  //   
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

  //   
  addComment: (projectId, commentData) => apiRequest(`/api/projects/${projectId}/feedback/comments/`, {
    method: 'POST',
    body: JSON.stringify(commentData)
  }),

  //   
  checkEncodingStatus: (projectId) => apiRequest(`/api/projects/${projectId}/feedback/encoding-status/`)
};

// 4.   
export const errorHandler = {
  //   
  handle: (error, context) => {
    console.error(`Error in ${context}:`, error);

    //  
    if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
      //   
      return refreshToken();
    }

    //  
    if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
      return {
        error: true,
        message: ' .',
        code: 'FORBIDDEN'
      };
    }

    //  
    if (error.message?.includes('500') || error.message?.includes('Internal Server Error')) {
      return {
        error: true,
        message: '  .    .',
        code: 'SERVER_ERROR'
      };
    }

    //  
    if (error.message?.includes('NetworkError') || error.message?.includes('fetch')) {
      return {
        error: true,
        message: '  .',
        code: 'NETWORK_ERROR'
      };
    }

    //  
    return {
      error: true,
      message: error.message || '    .',
      code: 'UNKNOWN_ERROR'
    };
  },

  //  
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

//  
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

//  
export const examples = {
  //   
  createProject: async () => {
    try {
      const projectData = {
        name: ' ',
        manager: '',
        consumer: 'ABC ',
        description: ' ',
        process: [
          { key: 'basic_plan', startDate: '2025-01-01', endDate: '2025-01-07' },
          { key: 'story_board', startDate: '2025-01-08', endDate: '2025-01-14' }
        ]
      };

      const result = await projectAPI.create(projectData);
      console.log('  :', result);
      return result;
    } catch (error) {
      const handled = errorHandler.handle(error, 'createProject');
      console.error('  :', handled);
      return handled;
    }
  },

  //    ( )
  uploadFeedbackWithRetry: async (projectId, file) => {
    return errorHandler.retry(
      () => feedbackAPI.uploadFeedback(projectId, file),
      3,  // 3 
      2000  // 2 
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