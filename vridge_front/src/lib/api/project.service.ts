import { APIClient } from './base';
import type {
  APIResponse,
  PaginatedResponse,
  Project,
  ProjectDetail,
  ProjectMember,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectStatus
} from '@/types';

export interface ProjectQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: ProjectStatus;
  ordering?: 'created_at' | '-created_at' | 'updated_at' | '-updated_at' | 'title' | '-title';
}

export interface InviteMemberRequest {
  email: string;
  role: 'admin' | 'member' | 'viewer';
}

export interface InviteResponse {
  id: number;
  project_id: number;
  invited_email: string;
  role: string;
  token: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

/**
 * VideoPlanet   API 
 * 2025  : TanStack Query  
 * Zustand    
 */
export class ProjectService extends APIClient {
  
  /**
   *   
   * - , , ,  
   * - TanStack Query queryKey    
   */
  async getProjects(params?: ProjectQueryParams): Promise<APIResponse<PaginatedResponse<Project>>> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value.toString());
        }
      });
    }

    const endpoint = `/api/projects/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.get<PaginatedResponse<Project>>(endpoint);
  }

  /**
   *    
   * -  ,    
   */
  async getProjectDetail(projectId: number): Promise<APIResponse<ProjectDetail>> {
    return this.get<ProjectDetail>(`/api/projects/detail/${projectId}/`);
  }

  /**
   *  
   * -      
   * -    
   */
  async createProject(data: CreateProjectRequest): Promise<APIResponse<Project>> {
    return this.post<Project>('/api/projects/create/', data);
  }

  /**
   *   
   * -   
   * -   
   */
  async updateProject(
    projectId: number, 
    data: UpdateProjectRequest
  ): Promise<APIResponse<Project>> {
    return this.put<Project>(`/api/projects/detail/${projectId}/`, data);
  }

  /**
   *  
   * -   (archived  )
   * -    
   */
  async deleteProject(projectId: number): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/projects/detail/${projectId}/`);
  }

  /**
   *  
   * -      
   */
  async archiveProject(projectId: number): Promise<APIResponse<Project>> {
    return this.patch<Project>(`/api/projects/detail/${projectId}/`, {
      status: 'archived' as ProjectStatus
    });
  }

  /**
   *  
   * -     
   */
  async restoreProject(projectId: number): Promise<APIResponse<Project>> {
    return this.patch<Project>(`/api/projects/detail/${projectId}/`, {
      status: 'planning' as ProjectStatus
    });
  }

  /**
   *   
   * -    
   * -    
   */
  async inviteMember(
    projectId: number, 
    data: InviteMemberRequest
  ): Promise<APIResponse<InviteResponse>> {
    return this.post<InviteResponse>(`/api/projects/${projectId}/invitations/`, data);
  }

  /**
   *    
   */
  async getProjectMembers(projectId: number): Promise<APIResponse<ProjectMember[]>> {
    const response = await this.get<ProjectDetail>(`/api/projects/detail/${projectId}/`);
    if (response.success && response.data) {
      return {
        success: true,
        data: response.data.members
      };
    }
    return response as unknown as APIResponse<ProjectMember[]>;
  }

  /**
   *   
   */
  async removeMember(projectId: number, memberId: number): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/projects/${projectId}/members/${memberId}/`);
  }

  /**
   *    
   */
  async updateMemberRole(
    projectId: number, 
    memberId: number, 
    role: 'admin' | 'member' | 'viewer'
  ): Promise<APIResponse<ProjectDetail['members'][0]>> {
    return this.patch<ProjectDetail['members'][0]>(
      `/api/projects/${projectId}/members/${memberId}/`,
      { role }
    );
  }

  /**
   *     
   */
  async getMyProjects(params?: Omit<ProjectQueryParams, 'owner'>): Promise<APIResponse<PaginatedResponse<Project>>> {
    const queryParams = new URLSearchParams();
    queryParams.append('my_projects', 'true');
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value.toString());
        }
      });
    }

    const endpoint = `/api/projects/?${queryParams.toString()}`;
    return this.get<PaginatedResponse<Project>>(endpoint);
  }

  /**
   *   /
   */
  async toggleFavorite(projectId: number): Promise<APIResponse<{ is_favorite: boolean }>> {
    return this.post<{ is_favorite: boolean }>(`/api/projects/${projectId}/favorite/`);
  }

  /**
   *  
   * -       
   */
  async duplicateProject(
    projectId: number, 
    newTitle?: string
  ): Promise<APIResponse<Project>> {
    return this.post<Project>(`/api/projects/${projectId}/duplicate/`, {
      title: newTitle
    });
  }

  /**
   *   
   * -   
   */
  async updateProjectStatus(
    projectId: number, 
    status: ProjectStatus
  ): Promise<APIResponse<Project>> {
    return this.patch<Project>(`/api/projects/detail/${projectId}/`, { status });
  }

  /**
   *   
   */
  async updateProjectProgress(
    projectId: number, 
    progress: number
  ): Promise<APIResponse<Project>> {
    if (progress < 0 || progress > 100) {
      return {
        success: false,
        error: {
          message: ' 0-100   .',
          code: 'INVALID_PROGRESS'
        }
      };
    }

    return this.patch<Project>(`/api/projects/detail/${projectId}/`, { progress });
  }

  /**
   *   
   * -   
   */
  async searchProjectSuggestions(query: string): Promise<APIResponse<string[]>> {
    if (!query || query.length < 2) {
      return { success: true, data: [] };
    }

    return this.get<string[]>(`/api/projects/search-suggestions/?q=${encodeURIComponent(query)}`);
  }

  /**
   *   
   * -   
   */
  async getProjectStats(): Promise<APIResponse<{
    total_projects: number;
    projects_by_status: Record<ProjectStatus, number>;
    recent_activity: Array<{
      id: number;
      title: string;
      action: string;
      timestamp: string;
    }>;
  }>> {
    return this.get('/api/projects/stats/');
  }

  /**
   * TanStack Query  
   */

  /**
   * Query Key  
   * - TanStack Query queryKey 
   */
  static generateQueryKey(type: string, params?: any): string[] {
    const baseKey = ['projects', type];
    if (params) {
      baseKey.push(JSON.stringify(params));
    }
    return baseKey;
  }

  /**
   *    
   */
  static getCacheInvalidationKeys() {
    return {
      all: ['projects'],
      lists: ['projects', 'list'],
      details: ['projects', 'detail'],
      stats: ['projects', 'stats'],
      project: (id: number) => ['projects', 'detail', id],
      projectMembers: (id: number) => ['projects', 'detail', id, 'members'],
    };
  }

  /**
   *   
   */
  static handleProjectError(error: any): { message: string; actionable: boolean } {
    if (error?.code === 'PROJECT_NOT_FOUND') {
      return {
        message: '   .',
        actionable: false
      };
    }

    if (error?.code === 'PERMISSION_DENIED') {
      return {
        message: '    .',
        actionable: false
      };
    }

    if (error?.code === 'DUPLICATE_PROJECT_TITLE') {
      return {
        message: '    .',
        actionable: true
      };
    }

    return {
      message: error?.message || '    .',
      actionable: true
    };
  }
}

//  
export const projectService = new ProjectService();

// TanStack Query     
export const projectQueryKeys = {
  all: ['projects'] as const,
  lists: () => [...projectQueryKeys.all, 'list'] as const,
  list: (params?: ProjectQueryParams) => [...projectQueryKeys.lists(), params] as const,
  details: () => [...projectQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...projectQueryKeys.details(), id] as const,
  stats: () => [...projectQueryKeys.all, 'stats'] as const,
  myProjects: (params?: ProjectQueryParams) => [...projectQueryKeys.all, 'my', params] as const,
};