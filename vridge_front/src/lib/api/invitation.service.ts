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
 *     API  
 */
class InvitationService {
  private readonly endpoint = '/api/invitations';

  /**
   *  
   */
  async sendInvitation(data: SendInvitationData): Promise<APIResponse<Invitation>> {
    return apiClient.post<Invitation>(`${this.endpoint}/`, data);
  }

  /**
   *    
   */
  async getReceivedInvitations(): Promise<APIResponse<Invitation[]>> {
    return apiClient.get<Invitation[]>(`${this.endpoint}/received/`);
  }

  /**
   *    
   */
  async getSentInvitations(): Promise<APIResponse<Invitation[]>> {
    return apiClient.get<Invitation[]>(`${this.endpoint}/sent/`);
  }

  /**
   *   
   */
  async getInvitation(id: number): Promise<APIResponse<Invitation>> {
    return apiClient.get<Invitation>(`${this.endpoint}/${id}/`);
  }

  /**
   *   (/)
   */
  async respondToInvitation(id: number, data: UpdateInvitationData): Promise<APIResponse<Invitation>> {
    return apiClient.patch<Invitation>(`${this.endpoint}/${id}/respond/`, data);
  }

  /**
   *  
   */
  async cancelInvitation(id: number): Promise<APIResponse<void>> {
    return apiClient.patch<void>(`${this.endpoint}/${id}/cancel/`);
  }

  /**
   *  
   */
  async resendInvitation(id: number): Promise<APIResponse<Invitation>> {
    return apiClient.post<Invitation>(`${this.endpoint}/${id}/resend/`);
  }

  /**
   *   
   */
  async getTeamMembers(projectId?: number): Promise<APIResponse<TeamMember[]>> {
    const url = projectId 
      ? `${this.endpoint}/team-members/?project_id=${projectId}`
      : `${this.endpoint}/team-members/`;
    return apiClient.get<TeamMember[]>(url);
  }

  /**
   *  
   */
  async removeTeamMember(memberId: number, projectId?: number): Promise<APIResponse<void>> {
    const url = projectId 
      ? `${this.endpoint}/team-members/${memberId}/?project_id=${projectId}`
      : `${this.endpoint}/team-members/${memberId}/`;
    return apiClient.delete<void>(url);
  }

  /**
   *    (  )
   */
  async getFriends(): Promise<APIResponse<Friend[]>> {
    return apiClient.get<Friend[]>(`${this.endpoint}/friends/`);
  }

  /**
   *   ()
   */
  async addFriend(email: string): Promise<APIResponse<Friend>> {
    return apiClient.post<Friend>(`${this.endpoint}/friends/`, { email });
  }

  /**
   *  
   */
  async removeFriend(friendId: number): Promise<APIResponse<void>> {
    return apiClient.delete<void>(`${this.endpoint}/friends/${friendId}/`);
  }

  /**
   *   
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
   *   
   */
  async searchUserByEmail(email: string): Promise<APIResponse<{
    exists: boolean;
    name?: string;
    avatar?: string;
  }>> {
    return apiClient.get(`${this.endpoint}/search/?email=${encodeURIComponent(email)}`);
  }
}

//   export
export const invitationService = new InvitationService();