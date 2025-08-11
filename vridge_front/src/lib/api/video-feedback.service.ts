import { apiClient } from './base';
import type { APIResponse } from '@/types';
import type {
  VideoFile,
  TimelineFeedback,
  CreateTimelineFeedbackData,
  UpdateTimelineFeedbackData,
  VideoSession,
  CreateVideoSessionData,
  RealtimeComment,
  CreateRealtimeCommentData,
  VideoFeedbackStats,
  FeedbackFrame,
  User
} from '@/types/video-feedback';

/**
 *   API 
 *   ,  ,     .
 */
class VideoFeedbackService {
  private readonly videoEndpoint = '/api/videos';
  private readonly feedbackEndpoint = '/api/video-feedbacks';
  private readonly sessionEndpoint = '/api/video-sessions';
  private readonly commentEndpoint = '/api/realtime-comments';

  // ==========   ==========
  
  /**
   *    
   */
  async getVideos(projectId?: number): Promise<APIResponse<VideoFile[]>> {
    const url = projectId 
      ? `${this.videoEndpoint}/?project_id=${projectId}`
      : `${this.videoEndpoint}/`;
    return apiClient.get<VideoFile[]>(url);
  }

  /**
   *    
   */
  async getVideo(id: string): Promise<APIResponse<VideoFile>> {
    return apiClient.get<VideoFile>(`${this.videoEndpoint}/${id}/`);
  }

  /**
   *   
   */
  async uploadVideo(formData: FormData): Promise<APIResponse<VideoFile>> {
    return apiClient.post<VideoFile>(`${this.videoEndpoint}/upload/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  // ==========   ==========

  /**
   *     
   */
  async getVideoFeedbacks(videoId: string, filters?: {
    category?: string;
    priority?: string;
    status?: string;
    author?: number;
  }): Promise<APIResponse<TimelineFeedback[]>> {
    let url = `${this.feedbackEndpoint}/?video_id=${videoId}`;
    
    if (filters) {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });
      const queryString = params.toString();
      if (queryString) url += `&${queryString}`;
    }
    
    return apiClient.get<TimelineFeedback[]>(url);
  }

  /**
   *     
   */
  async getFeedbacksByTimeRange(
    videoId: string, 
    startTime: number, 
    endTime: number
  ): Promise<APIResponse<TimelineFeedback[]>> {
    return apiClient.get<TimelineFeedback[]>(
      `${this.feedbackEndpoint}/?video_id=${videoId}&start_time=${startTime}&end_time=${endTime}`
    );
  }

  /**
   *  
   */
  async createFeedback(data: CreateTimelineFeedbackData): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.post<TimelineFeedback>(`${this.feedbackEndpoint}/`, data);
  }

  /**
   *  
   */
  async updateFeedback(id: string, data: UpdateTimelineFeedbackData): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.patch<TimelineFeedback>(`${this.feedbackEndpoint}/${id}/`, data);
  }

  /**
   *  
   */
  async deleteFeedback(id: string): Promise<APIResponse<void>> {
    return apiClient.delete<void>(`${this.feedbackEndpoint}/${id}/`);
  }

  /**
   *    (/ )
   */
  async resolveFeedback(id: string, resolution?: string): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.patch<TimelineFeedback>(`${this.feedbackEndpoint}/${id}/resolve/`, {
      resolution
    });
  }

  /**
   *   
   */
  async addFeedbackReply(feedbackId: string, content: string, mentions?: number[]): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.post<TimelineFeedback>(`${this.feedbackEndpoint}/${feedbackId}/replies/`, {
      content,
      mentions
    });
  }

  // ==========    ==========

  /**
   *    ( )
   */
  async createVideoSession(data: CreateVideoSessionData): Promise<APIResponse<VideoSession>> {
    return apiClient.post<VideoSession>(`${this.sessionEndpoint}/`, data);
  }

  /**
   *    
   */
  async getVideoSessions(videoId?: string): Promise<APIResponse<VideoSession[]>> {
    const url = videoId 
      ? `${this.sessionEndpoint}/?video_id=${videoId}`
      : `${this.sessionEndpoint}/`;
    return apiClient.get<VideoSession[]>(url);
  }

  /**
   *    
   */
  async getVideoSession(id: string): Promise<APIResponse<VideoSession>> {
    return apiClient.get<VideoSession>(`${this.sessionEndpoint}/${id}/`);
  }

  /**
   *  
   */
  async joinSession(id: string): Promise<APIResponse<VideoSession>> {
    return apiClient.post<VideoSession>(`${this.sessionEndpoint}/${id}/join/`);
  }

  /**
   *  
   */
  async leaveSession(id: string): Promise<APIResponse<void>> {
    return apiClient.post<void>(`${this.sessionEndpoint}/${id}/leave/`);
  }

  /**
   *   
   */
  async syncPlayback(sessionId: string, playbackState: {
    current_time: number;
    is_playing: boolean;
    playback_rate: number;
  }): Promise<APIResponse<void>> {
    return apiClient.post<void>(`${this.sessionEndpoint}/${sessionId}/sync-playback/`, playbackState);
  }

  // ==========   ==========

  /**
   *    
   */
  async getSessionComments(sessionId: string, limit?: number): Promise<APIResponse<RealtimeComment[]>> {
    const url = limit 
      ? `${this.commentEndpoint}/?session_id=${sessionId}&limit=${limit}`
      : `${this.commentEndpoint}/?session_id=${sessionId}`;
    return apiClient.get<RealtimeComment[]>(url);
  }

  /**
   *   
   */
  async createComment(data: CreateRealtimeCommentData): Promise<APIResponse<RealtimeComment>> {
    return apiClient.post<RealtimeComment>(`${this.commentEndpoint}/`, data);
  }

  /**
   *    
   */
  async getCommentsAtTime(sessionId: string, timestamp: number, range?: number): Promise<APIResponse<RealtimeComment[]>> {
    const rangeParam = range ? `&range=${range}` : '';
    return apiClient.get<RealtimeComment[]>(
      `${this.commentEndpoint}/?session_id=${sessionId}&timestamp=${timestamp}${rangeParam}`
    );
  }

  // ==========   () ==========

  /**
   *    
   */
  async captureFrame(videoId: string, timestamp: number): Promise<APIResponse<FeedbackFrame>> {
    return apiClient.post<FeedbackFrame>(`${this.videoEndpoint}/${videoId}/capture-frame/`, {
      timestamp
    });
  }

  /**
   *   
   */
  async addFrameAnnotation(frameId: string, annotation: {
    type: 'arrow' | 'circle' | 'rectangle' | 'text';
    position: { x: number; y: number; width?: number; height?: number };
    color: string;
    content?: string;
  }): Promise<APIResponse<FeedbackFrame>> {
    return apiClient.post<FeedbackFrame>(`${this.videoEndpoint}/frames/${frameId}/annotations/`, annotation);
  }

  // ==========    ==========

  /**
   *    
   */
  async getVideoFeedbackStats(videoId: string): Promise<APIResponse<VideoFeedbackStats>> {
    return apiClient.get<VideoFeedbackStats>(`${this.videoEndpoint}/${videoId}/feedback-stats/`);
  }

  /**
   *     
   */
  async getHotspots(videoId: string, minFeedbacks: number = 2): Promise<APIResponse<{
    timestamp: number;
    feedback_count: number;
    comment_count: number;
    categories: string[];
  }[]>> {
    return apiClient.get(`${this.videoEndpoint}/${videoId}/hotspots/?min_feedbacks=${minFeedbacks}`);
  }

  // ==========   ==========

  /**
   *   (   )
   */
  async inviteToVideo(videoId: string, emails: string[], message?: string): Promise<APIResponse<void>> {
    return apiClient.post<void>(`${this.videoEndpoint}/${videoId}/invite/`, {
      emails,
      message
    });
  }

  /**
   *     
   */
  async getMentionableUsers(videoId: string): Promise<APIResponse<User[]>> {
    return apiClient.get<User[]>(`${this.videoEndpoint}/${videoId}/mentionable-users/`);
  }

  // ==========  ==========

  /**
   *    (PDF)
   */
  async exportFeedbackReport(videoId: string, format: 'pdf' | 'excel' = 'pdf'): Promise<APIResponse<{ download_url: string }>> {
    return apiClient.post<{ download_url: string }>(`${this.videoEndpoint}/${videoId}/export-feedback/`, {
      format
    });
  }

  /**
   *    
   */
  async exportTimeline(videoId: string): Promise<APIResponse<{ download_url: string }>> {
    return apiClient.post<{ download_url: string }>(`${this.videoEndpoint}/${videoId}/export-timeline/`);
  }
}

//   export
export const videoFeedbackService = new VideoFeedbackService();