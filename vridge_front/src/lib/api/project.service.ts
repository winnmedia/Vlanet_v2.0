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
 * VideoPlanet 프로젝트 관련 API 서비스
 * 2025년 최신 패턴: TanStack Query와 통합 최적화
 * Zustand와 분리된 서버 상태 관리
 */
export class ProjectService extends APIClient {
  
  /**
   * 프로젝트 목록 조회
   * - 페이지네이션, 검색, 필터링, 정렬 지원
   * - TanStack Query의 queryKey로 사용할 수 있는 구조
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
   * 프로젝트 상세 정보 조회
   * - 멤버 목록, 파일 목록 등 포함
   */
  async getProjectDetail(projectId: number): Promise<APIResponse<ProjectDetail>> {
    return this.get<ProjectDetail>(`/api/projects/detail/${projectId}/`);
  }

  /**
   * 프로젝트 생성
   * - 원자적 처리로 관련 객체 모두 생성
   * - 중복 방지 로직 포함
   */
  async createProject(data: CreateProjectRequest): Promise<APIResponse<Project>> {
    return this.post<Project>('/api/projects/create/', data);
  }

  /**
   * 프로젝트 정보 수정
   * - 부분 업데이트 지원
   * - 권한 확인 포함
   */
  async updateProject(
    projectId: number, 
    data: UpdateProjectRequest
  ): Promise<APIResponse<Project>> {
    return this.put<Project>(`/api/projects/detail/${projectId}/`, data);
  }

  /**
   * 프로젝트 삭제
   * - 소프트 삭제 (archived 상태로 변경)
   * - 완전 삭제는 관리자만 가능
   */
  async deleteProject(projectId: number): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/projects/detail/${projectId}/`);
  }

  /**
   * 프로젝트 아카이브
   * - 소프트 삭제 대신 아카이브 상태로 변경
   */
  async archiveProject(projectId: number): Promise<APIResponse<Project>> {
    return this.patch<Project>(`/api/projects/detail/${projectId}/`, {
      status: 'archived' as ProjectStatus
    });
  }

  /**
   * 프로젝트 복원
   * - 아카이브된 프로젝트를 활성 상태로 복원
   */
  async restoreProject(projectId: number): Promise<APIResponse<Project>> {
    return this.patch<Project>(`/api/projects/detail/${projectId}/`, {
      status: 'planning' as ProjectStatus
    });
  }

  /**
   * 프로젝트 멤버 초대
   * - 이메일 기반 초대 시스템
   * - 역할 기반 권한 관리
   */
  async inviteMember(
    projectId: number, 
    data: InviteMemberRequest
  ): Promise<APIResponse<InviteResponse>> {
    return this.post<InviteResponse>(`/api/projects/${projectId}/invitations/`, data);
  }

  /**
   * 프로젝트 멤버 목록 조회
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
   * 프로젝트 멤버 제거
   */
  async removeMember(projectId: number, memberId: number): Promise<APIResponse<{ message: string }>> {
    return this.delete<{ message: string }>(`/api/projects/${projectId}/members/${memberId}/`);
  }

  /**
   * 프로젝트 멤버 역할 변경
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
   * 내가 속한 프로젝트 목록 조회
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
   * 프로젝트 즐겨찾기 추가/제거
   */
  async toggleFavorite(projectId: number): Promise<APIResponse<{ is_favorite: boolean }>> {
    return this.post<{ is_favorite: boolean }>(`/api/projects/${projectId}/favorite/`);
  }

  /**
   * 프로젝트 복제
   * - 기존 프로젝트 설정을 복사해서 새 프로젝트 생성
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
   * 프로젝트 상태 업데이트
   * - 워크플로우 상태 변경
   */
  async updateProjectStatus(
    projectId: number, 
    status: ProjectStatus
  ): Promise<APIResponse<Project>> {
    return this.patch<Project>(`/api/projects/detail/${projectId}/`, { status });
  }

  /**
   * 프로젝트 진행률 업데이트
   */
  async updateProjectProgress(
    projectId: number, 
    progress: number
  ): Promise<APIResponse<Project>> {
    if (progress < 0 || progress > 100) {
      return {
        success: false,
        error: {
          message: '진행률은 0-100 사이의 값이어야 합니다.',
          code: 'INVALID_PROGRESS'
        }
      };
    }

    return this.patch<Project>(`/api/projects/detail/${projectId}/`, { progress });
  }

  /**
   * 프로젝트 검색 자동완성
   * - 실시간 검색 제안
   */
  async searchProjectSuggestions(query: string): Promise<APIResponse<string[]>> {
    if (!query || query.length < 2) {
      return { success: true, data: [] };
    }

    return this.get<string[]>(`/api/projects/search-suggestions/?q=${encodeURIComponent(query)}`);
  }

  /**
   * 프로젝트 통계 조회
   * - 대시보드용 통계 데이터
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
   * TanStack Query용 유틸리티 메서드들
   */

  /**
   * Query Key 생성 헬퍼
   * - TanStack Query의 queryKey 표준화
   */
  static generateQueryKey(type: string, params?: any): string[] {
    const baseKey = ['projects', type];
    if (params) {
      baseKey.push(JSON.stringify(params));
    }
    return baseKey;
  }

  /**
   * 캐시 무효화 키 패턴
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
   * 에러 핸들링 헬퍼
   */
  static handleProjectError(error: any): { message: string; actionable: boolean } {
    if (error?.code === 'PROJECT_NOT_FOUND') {
      return {
        message: '프로젝트를 찾을 수 없습니다.',
        actionable: false
      };
    }

    if (error?.code === 'PERMISSION_DENIED') {
      return {
        message: '이 프로젝트에 대한 권한이 없습니다.',
        actionable: false
      };
    }

    if (error?.code === 'DUPLICATE_PROJECT_TITLE') {
      return {
        message: '같은 이름의 프로젝트가 이미 존재합니다.',
        actionable: true
      };
    }

    return {
      message: error?.message || '프로젝트 작업 중 오류가 발생했습니다.',
      actionable: true
    };
  }
}

// 싱글톤 인스턴스
export const projectService = new ProjectService();

// TanStack Query와 함께 사용할 수 있는 헬퍼들
export const projectQueryKeys = {
  all: ['projects'] as const,
  lists: () => [...projectQueryKeys.all, 'list'] as const,
  list: (params?: ProjectQueryParams) => [...projectQueryKeys.lists(), params] as const,
  details: () => [...projectQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...projectQueryKeys.details(), id] as const,
  stats: () => [...projectQueryKeys.all, 'stats'] as const,
  myProjects: (params?: ProjectQueryParams) => [...projectQueryKeys.all, 'my', params] as const,
};