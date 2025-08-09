import { apiClient } from './base';
import type { APIResponse } from '@/types';

export interface Invitation {
  id: number;
  sender_id: number;
  sender_email: string;
  sender_name: string;
  recipient_email: string;
  project_id?: number;
  project_title?: string;
  status: 'pending' | 'accepted' | 'declined' | 'cancelled';
  message?: string;
  created_at: string;
  updated_at: string;
  expires_at: string;
}

export interface SendInvitationData {
  recipient_email: string;
  project_id?: number;
  message?: string;
}

export interface UpdateInvitationData {
  status: 'accepted' | 'declined';
  message?: string;
}

export interface TeamMember {
  id: number;
  email: string;
  name: string;
  role: string;
  avatar?: string;
  joined_at: string;
  last_active: string;
  status: 'active' | 'inactive';
}

export interface Friend {
  id: number;
  email: string;
  name: string;
  avatar?: string;
  added_at: string;
  last_interaction: string;
  projects_shared: number;
}

/**
 * 초대 및 팀 관리 API 서비스 클래스
 */
class InvitationService {
  private readonly endpoint = '/api/invitations';

  /**
   * 초대장 발송
   */
  async sendInvitation(data: SendInvitationData): Promise<APIResponse<Invitation>> {
    return apiClient.post<Invitation>(`${this.endpoint}/`, data);
  }

  /**
   * 받은 초대장 목록 조회
   */
  async getReceivedInvitations(): Promise<APIResponse<Invitation[]>> {
    return apiClient.get<Invitation[]>(`${this.endpoint}/received/`);
  }

  /**
   * 보낸 초대장 목록 조회
   */
  async getSentInvitations(): Promise<APIResponse<Invitation[]>> {
    return apiClient.get<Invitation[]>(`${this.endpoint}/sent/`);
  }

  /**
   * 특정 초대장 조회
   */
  async getInvitation(id: number): Promise<APIResponse<Invitation>> {
    return apiClient.get<Invitation>(`${this.endpoint}/${id}/`);
  }

  /**
   * 초대장 응답 (수락/거절)
   */
  async respondToInvitation(id: number, data: UpdateInvitationData): Promise<APIResponse<Invitation>> {
    return apiClient.patch<Invitation>(`${this.endpoint}/${id}/respond/`, data);
  }

  /**
   * 초대장 취소
   */
  async cancelInvitation(id: number): Promise<APIResponse<void>> {
    return apiClient.patch<void>(`${this.endpoint}/${id}/cancel/`);
  }

  /**
   * 초대장 재발송
   */
  async resendInvitation(id: number): Promise<APIResponse<Invitation>> {
    return apiClient.post<Invitation>(`${this.endpoint}/${id}/resend/`);
  }

  /**
   * 팀원 목록 조회
   */
  async getTeamMembers(projectId?: number): Promise<APIResponse<TeamMember[]>> {
    const url = projectId 
      ? `${this.endpoint}/team-members/?project_id=${projectId}`
      : `${this.endpoint}/team-members/`;
    return apiClient.get<TeamMember[]>(url);
  }

  /**
   * 팀원 제거
   */
  async removeTeamMember(memberId: number, projectId?: number): Promise<APIResponse<void>> {
    const url = projectId 
      ? `${this.endpoint}/team-members/${memberId}/?project_id=${projectId}`
      : `${this.endpoint}/team-members/${memberId}/`;
    return apiClient.delete<void>(url);
  }

  /**
   * 친구 목록 조회 (최근 초대한 사람들)
   */
  async getFriends(): Promise<APIResponse<Friend[]>> {
    return apiClient.get<Friend[]>(`${this.endpoint}/friends/`);
  }

  /**
   * 친구 추가 (이메일로)
   */
  async addFriend(email: string): Promise<APIResponse<Friend>> {
    return apiClient.post<Friend>(`${this.endpoint}/friends/`, { email });
  }

  /**
   * 친구 제거
   */
  async removeFriend(friendId: number): Promise<APIResponse<void>> {
    return apiClient.delete<void>(`${this.endpoint}/friends/${friendId}/`);
  }

  /**
   * 초대 통계 조회
   */
  async getInvitationStats(): Promise<APIResponse<{
    total_sent: number;
    total_received: number;
    pending_sent: number;
    pending_received: number;
    accepted_sent: number;
    accepted_received: number;
    declined_sent: number;
    declined_received: number;
  }>> {
    return apiClient.get(`${this.endpoint}/stats/`);
  }

  /**
   * 이메일로 사용자 검색
   */
  async searchUserByEmail(email: string): Promise<APIResponse<{
    exists: boolean;
    name?: string;
    avatar?: string;
  }>> {
    return apiClient.get(`${this.endpoint}/search/?email=${encodeURIComponent(email)}`);
  }
}

// 싱글톤 인스턴스 export
export const invitationService = new InvitationService();