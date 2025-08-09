import { apiClient } from './base';
import type { APIResponse } from '@/types';

export interface Feedback {
  id: number;
  title: string;
  content: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'resolved';
  created_at: string;
  updated_at: string;
}

export interface CreateFeedbackData {
  title: string;
  content: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
}

export interface UpdateFeedbackData extends Partial<CreateFeedbackData> {
  status?: 'pending' | 'in_progress' | 'resolved';
}

export interface FeedbackFilters {
  status?: 'pending' | 'in_progress' | 'resolved';
  category?: string;
  priority?: 'low' | 'medium' | 'high';
}

/**
 * Feedback API 서비스 클래스
 * 피드백 관리 CRUD 기능을 제공합니다.
 */
class FeedbackService {
  private readonly endpoint = '/api/feedbacks';

  /**
   * 모든 피드백 목록 조회
   */
  async getFeedbacks(filters?: FeedbackFilters): Promise<APIResponse<Feedback[]>> {
    let url = `${this.endpoint}/`;
    
    if (filters) {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.category) params.append('category', filters.category);
      if (filters.priority) params.append('priority', filters.priority);
      
      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }
    
    return apiClient.get<Feedback[]>(url);
  }

  /**
   * 특정 피드백 조회
   */
  async getFeedback(id: number): Promise<APIResponse<Feedback>> {
    return apiClient.get<Feedback>(`${this.endpoint}/${id}/`);
  }

  /**
   * 새 피드백 생성
   */
  async createFeedback(data: CreateFeedbackData): Promise<APIResponse<Feedback>> {
    return apiClient.post<Feedback>(`${this.endpoint}/`, data);
  }

  /**
   * 피드백 전체 업데이트
   */
  async updateFeedback(id: number, data: CreateFeedbackData & { status?: 'pending' | 'in_progress' | 'resolved' }): Promise<APIResponse<Feedback>> {
    return apiClient.put<Feedback>(`${this.endpoint}/${id}/`, data);
  }

  /**
   * 피드백 부분 업데이트
   */
  async patchFeedback(id: number, data: UpdateFeedbackData): Promise<APIResponse<Feedback>> {
    return apiClient.patch<Feedback>(`${this.endpoint}/${id}/`, data);
  }

  /**
   * 피드백 삭제
   */
  async deleteFeedback(id: number): Promise<APIResponse<void>> {
    return apiClient.delete<void>(`${this.endpoint}/${id}/`);
  }

  /**
   * 피드백 상태 변경
   */
  async updateFeedbackStatus(id: number, status: 'pending' | 'in_progress' | 'resolved'): Promise<APIResponse<Feedback>> {
    return apiClient.patch<Feedback>(`${this.endpoint}/${id}/`, { status });
  }

  /**
   * 카테고리별 피드백 조회
   */
  async getFeedbacksByCategory(category: string): Promise<APIResponse<Feedback[]>> {
    return apiClient.get<Feedback[]>(`${this.endpoint}/?category=${category}`);
  }

  /**
   * 우선순위별 피드백 조회
   */
  async getFeedbacksByPriority(priority: 'low' | 'medium' | 'high'): Promise<APIResponse<Feedback[]>> {
    return apiClient.get<Feedback[]>(`${this.endpoint}/?priority=${priority}`);
  }

  /**
   * 상태별 피드백 조회
   */
  async getFeedbacksByStatus(status: 'pending' | 'in_progress' | 'resolved'): Promise<APIResponse<Feedback[]>> {
    return apiClient.get<Feedback[]>(`${this.endpoint}/?status=${status}`);
  }

  /**
   * 피드백 통계 조회
   */
  async getFeedbackStats(): Promise<APIResponse<{
    total: number;
    pending: number;
    in_progress: number;
    resolved: number;
    by_category: Record<string, number>;
    by_priority: Record<string, number>;
  }>> {
    return apiClient.get(`${this.endpoint}/stats/`);
  }
}

// 싱글톤 인스턴스 export
export const feedbackService = new FeedbackService();