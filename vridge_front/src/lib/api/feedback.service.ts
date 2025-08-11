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
 * Feedback API  
 *   CRUD  .
 */
class FeedbackService {
  private readonly endpoint = '/api/feedbacks';

  /**
   *    
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
   *   
   */
  async getFeedback(id: number): Promise<APIResponse<Feedback>> {
    return apiClient.get<Feedback>(`${this.endpoint}/${id}/`);
  }

  /**
   *   
   */
  async createFeedback(data: CreateFeedbackData): Promise<APIResponse<Feedback>> {
    return apiClient.post<Feedback>(`${this.endpoint}/`, data);
  }

  /**
   *   
   */
  async updateFeedback(id: number, data: CreateFeedbackData & { status?: 'pending' | 'in_progress' | 'resolved' }): Promise<APIResponse<Feedback>> {
    return apiClient.put<Feedback>(`${this.endpoint}/${id}/`, data);
  }

  /**
   *   
   */
  async patchFeedback(id: number, data: UpdateFeedbackData): Promise<APIResponse<Feedback>> {
    return apiClient.patch<Feedback>(`${this.endpoint}/${id}/`, data);
  }

  /**
   *  
   */
  async deleteFeedback(id: number): Promise<APIResponse<void>> {
    return apiClient.delete<void>(`${this.endpoint}/${id}/`);
  }

  /**
   *   
   */
  async updateFeedbackStatus(id: number, status: 'pending' | 'in_progress' | 'resolved'): Promise<APIResponse<Feedback>> {
    return apiClient.patch<Feedback>(`${this.endpoint}/${id}/`, { status });
  }

  /**
   *   
   */
  async getFeedbacksByCategory(category: string): Promise<APIResponse<Feedback[]>> {
    return apiClient.get<Feedback[]>(`${this.endpoint}/?category=${category}`);
  }

  /**
   *   
   */
  async getFeedbacksByPriority(priority: 'low' | 'medium' | 'high'): Promise<APIResponse<Feedback[]>> {
    return apiClient.get<Feedback[]>(`${this.endpoint}/?priority=${priority}`);
  }

  /**
   *   
   */
  async getFeedbacksByStatus(status: 'pending' | 'in_progress' | 'resolved'): Promise<APIResponse<Feedback[]>> {
    return apiClient.get<Feedback[]>(`${this.endpoint}/?status=${status}`);
  }

  /**
   *   
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

//   export
export const feedbackService = new FeedbackService();