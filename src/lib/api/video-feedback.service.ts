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
 * 영상 피드백 API 서비스
 * 타임라인 기반 피드백, 실시간 협업, 영상 세션 관리 기능을 제공합니다.
 */
class VideoFeedbackService {
  private readonly videoEndpoint = '/api/videos';
  private readonly feedbackEndpoint = '/api/video-feedbacks';
  private readonly sessionEndpoint = '/api/video-sessions';
  private readonly commentEndpoint = '/api/realtime-comments';

  // ========== 영상 관리 ==========
  
  /**
   * 영상 파일 목록 조회
   */
  async getVideos(projectId?: number): Promise<APIResponse<VideoFile[]>> {
    const url = projectId 
      ? `${this.videoEndpoint}/?project_id=${projectId}`
      : `${this.videoEndpoint}/`;
    return apiClient.get<VideoFile[]>(url);
  }

  /**
   * 영상 파일 상세 조회
   */
  async getVideo(id: string): Promise<APIResponse<VideoFile>> {
    return apiClient.get<VideoFile>(`${this.videoEndpoint}/${id}/`);
  }

  /**
   * 영상 파일 업로드
   */
  async uploadVideo(formData: FormData): Promise<APIResponse<VideoFile>> {
    return apiClient.post<VideoFile>(`${this.videoEndpoint}/upload/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  // ========== 타임라인 피드백 ==========

  /**
   * 특정 영상의 모든 피드백 조회
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
   * 특정 타임스탬프 범위의 피드백 조회
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
   * 피드백 생성
   */
  async createFeedback(data: CreateTimelineFeedbackData): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.post<TimelineFeedback>(`${this.feedbackEndpoint}/`, data);
  }

  /**
   * 피드백 수정
   */
  async updateFeedback(id: string, data: UpdateTimelineFeedbackData): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.patch<TimelineFeedback>(`${this.feedbackEndpoint}/${id}/`, data);
  }

  /**
   * 피드백 삭제
   */
  async deleteFeedback(id: string): Promise<APIResponse<void>> {
    return apiClient.delete<void>(`${this.feedbackEndpoint}/${id}/`);
  }

  /**
   * 피드백 상태 변경 (해결/거부 등)
   */
  async resolveFeedback(id: string, resolution?: string): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.patch<TimelineFeedback>(`${this.feedbackEndpoint}/${id}/resolve/`, {
      resolution
    });
  }

  /**
   * 피드백에 답글 추가
   */
  async addFeedbackReply(feedbackId: string, content: string, mentions?: number[]): Promise<APIResponse<TimelineFeedback>> {
    return apiClient.post<TimelineFeedback>(`${this.feedbackEndpoint}/${feedbackId}/replies/`, {
      content,
      mentions
    });
  }

  // ========== 영상 세션 관리 ==========

  /**
   * 영상 세션 생성 (협업 세션)
   */
  async createVideoSession(data: CreateVideoSessionData): Promise<APIResponse<VideoSession>> {
    return apiClient.post<VideoSession>(`${this.sessionEndpoint}/`, data);
  }

  /**
   * 영상 세션 목록 조회
   */
  async getVideoSessions(videoId?: string): Promise<APIResponse<VideoSession[]>> {
    const url = videoId 
      ? `${this.sessionEndpoint}/?video_id=${videoId}`
      : `${this.sessionEndpoint}/`;
    return apiClient.get<VideoSession[]>(url);
  }

  /**
   * 특정 세션 상세 조회
   */
  async getVideoSession(id: string): Promise<APIResponse<VideoSession>> {
    return apiClient.get<VideoSession>(`${this.sessionEndpoint}/${id}/`);
  }

  /**
   * 세션에 참여
   */
  async joinSession(id: string): Promise<APIResponse<VideoSession>> {
    return apiClient.post<VideoSession>(`${this.sessionEndpoint}/${id}/join/`);
  }

  /**
   * 세션에서 나가기
   */
  async leaveSession(id: string): Promise<APIResponse<void>> {
    return apiClient.post<void>(`${this.sessionEndpoint}/${id}/leave/`);
  }

  /**
   * 재생 상태 동기화
   */
  async syncPlayback(sessionId: string, playbackState: {
    current_time: number;
    is_playing: boolean;
    playback_rate: number;
  }): Promise<APIResponse<void>> {
    return apiClient.post<void>(`${this.sessionEndpoint}/${sessionId}/sync-playback/`, playbackState);
  }

  // ========== 실시간 코멘트 ==========

  /**
   * 세션의 실시간 코멘트 조회
   */
  async getSessionComments(sessionId: string, limit?: number): Promise<APIResponse<RealtimeComment[]>> {
    const url = limit 
      ? `${this.commentEndpoint}/?session_id=${sessionId}&limit=${limit}`
      : `${this.commentEndpoint}/?session_id=${sessionId}`;
    return apiClient.get<RealtimeComment[]>(url);
  }

  /**
   * 실시간 코멘트 생성
   */
  async createComment(data: CreateRealtimeCommentData): Promise<APIResponse<RealtimeComment>> {
    return apiClient.post<RealtimeComment>(`${this.commentEndpoint}/`, data);
  }

  /**
   * 특정 타임스탬프의 코멘트 조회
   */
  async getCommentsAtTime(sessionId: string, timestamp: number, range?: number): Promise<APIResponse<RealtimeComment[]>> {
    const rangeParam = range ? `&range=${range}` : '';
    return apiClient.get<RealtimeComment[]>(
      `${this.commentEndpoint}/?session_id=${sessionId}&timestamp=${timestamp}${rangeParam}`
    );
  }

  // ========== 피드백 프레임 (스크린샷) ==========

  /**
   * 특정 타임스탬프의 프레임 캡처
   */
  async captureFrame(videoId: string, timestamp: number): Promise<APIResponse<FeedbackFrame>> {
    return apiClient.post<FeedbackFrame>(`${this.videoEndpoint}/${videoId}/capture-frame/`, {
      timestamp
    });
  }

  /**
   * 프레임에 주석 추가
   */
  async addFrameAnnotation(frameId: string, annotation: {
    type: 'arrow' | 'circle' | 'rectangle' | 'text';
    position: { x: number; y: number; width?: number; height?: number };
    color: string;
    content?: string;
  }): Promise<APIResponse<FeedbackFrame>> {
    return apiClient.post<FeedbackFrame>(`${this.videoEndpoint}/frames/${frameId}/annotations/`, annotation);
  }

  // ========== 통계 및 분석 ==========

  /**
   * 영상 피드백 통계 조회
   */
  async getVideoFeedbackStats(videoId: string): Promise<APIResponse<VideoFeedbackStats>> {
    return apiClient.get<VideoFeedbackStats>(`${this.videoEndpoint}/${videoId}/feedback-stats/`);
  }

  /**
   * 가장 많이 코멘트된 구간 조회
   */
  async getHotspots(videoId: string, minFeedbacks: number = 2): Promise<APIResponse<{
    timestamp: number;
    feedback_count: number;
    comment_count: number;
    categories: string[];
  }[]>> {
    return apiClient.get(`${this.videoEndpoint}/${videoId}/hotspots/?min_feedbacks=${minFeedbacks}`);
  }

  // ========== 팀 협업 ==========

  /**
   * 팀원 초대 (기존 초대 시스템 활용)
   */
  async inviteToVideo(videoId: string, emails: string[], message?: string): Promise<APIResponse<void>> {
    return apiClient.post<void>(`${this.videoEndpoint}/${videoId}/invite/`, {
      emails,
      message
    });
  }

  /**
   * 멘션 가능한 사용자 목록 조회
   */
  async getMentionableUsers(videoId: string): Promise<APIResponse<User[]>> {
    return apiClient.get<User[]>(`${this.videoEndpoint}/${videoId}/mentionable-users/`);
  }

  // ========== 내보내기 ==========

  /**
   * 피드백 리포트 내보내기 (PDF)
   */
  async exportFeedbackReport(videoId: string, format: 'pdf' | 'excel' = 'pdf'): Promise<APIResponse<{ download_url: string }>> {
    return apiClient.post<{ download_url: string }>(`${this.videoEndpoint}/${videoId}/export-feedback/`, {
      format
    });
  }

  /**
   * 피드백을 타임라인 형태로 내보내기
   */
  async exportTimeline(videoId: string): Promise<APIResponse<{ download_url: string }>> {
    return apiClient.post<{ download_url: string }>(`${this.videoEndpoint}/${videoId}/export-timeline/`);
  }
}

// 싱글톤 인스턴스 export
export const videoFeedbackService = new VideoFeedbackService();