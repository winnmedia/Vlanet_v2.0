/**
 * 영상 피드백 시스템 타입 정의
 * 타임라인 기반 피드백과 실시간 협업을 위한 데이터 구조
 */

// 기본 인터페이스
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  avatar?: string;
}

// 영상 파일 정보
export interface VideoFile {
  id: string;
  title: string;
  description?: string;
  file_url: string;
  thumbnail_url?: string;
  duration: number; // 초 단위
  resolution?: string;
  file_size: number;
  format: string;
  project_id?: number;
  created_at: string;
  updated_at: string;
}

// 피드백 카테고리 및 우선순위
export type FeedbackCategory = 
  | 'general'        // 일반
  | 'correction'     // 수정요청
  | 'question'       // 질문
  | 'approval'       // 승인
  | 'suggestion'     // 제안
  | 'technical'      // 기술적 이슈
  | 'creative';      // 창작 피드백

export type FeedbackPriority = 'low' | 'medium' | 'high' | 'urgent';

export type FeedbackStatus = 'active' | 'resolved' | 'declined';

// 타임라인 기반 피드백 (특정 시점에 대한 코멘트)
export interface TimelineFeedback {
  id: string;
  video_id: string;
  author: User;
  timestamp: number; // 초 단위 (영상에서의 위치)
  category: FeedbackCategory;
  priority: FeedbackPriority;
  status: FeedbackStatus;
  
  // 피드백 내용
  title: string;
  content: string;
  
  // 시각적 마킹 (선택사항 - 특정 영역 표시)
  position?: {
    x: number; // 영상 내 X 좌표 (0-1 비율)
    y: number; // 영상 내 Y 좌표 (0-1 비율)
    width?: number;
    height?: number;
  };
  
  // 첨부파일
  attachments?: {
    id: string;
    filename: string;
    url: string;
    type: 'image' | 'document' | 'audio';
  }[];
  
  // 답글
  replies?: TimelineFeedbackReply[];
  
  // 메타데이터
  mentions?: number[]; // 멘션된 사용자 ID들
  tags?: string[];
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  resolved_by?: User;
}

// 피드백에 대한 답글
export interface TimelineFeedbackReply {
  id: string;
  feedback_id: string;
  author: User;
  content: string;
  mentions?: number[];
  created_at: string;
  updated_at: string;
}

// 영상 세션 (여러 사용자가 동시에 보는 세션)
export interface VideoSession {
  id: string;
  video_id: string;
  title: string;
  host: User;
  participants: User[];
  is_active: boolean;
  
  // 세션 설정
  settings: {
    allow_comments: boolean;
    sync_playback: boolean; // 재생 동기화
    auto_pause_on_feedback: boolean; // 피드백 작성 시 자동 정지
  };
  
  // 현재 재생 상태 (동기화용)
  playback_state: {
    current_time: number;
    is_playing: boolean;
    playback_rate: number;
    last_updated: string;
    updated_by: number; // 사용자 ID
  };
  
  created_at: string;
  updated_at: string;
}

// 실시간 코멘트 (채팅 형태)
export interface RealtimeComment {
  id: string;
  session_id: string;
  author: User;
  content: string;
  timestamp?: number; // 영상 시점 (선택적)
  mentions?: number[];
  type: 'chat' | 'timestamp'; // 채팅 또는 특정 시점 코멘트
  created_at: string;
}

// 피드백 프레임 (특정 프레임/시점의 스크린샷)
export interface FeedbackFrame {
  id: string;
  video_id: string;
  timestamp: number;
  frame_url: string; // 스크린샷 URL
  annotations?: {
    id: string;
    type: 'arrow' | 'circle' | 'rectangle' | 'text';
    position: { x: number; y: number; width?: number; height?: number };
    color: string;
    content?: string;
  }[];
  created_at: string;
}

// API 요청/응답 타입들
export interface CreateTimelineFeedbackData {
  video_id: string;
  timestamp: number;
  category: FeedbackCategory;
  priority: FeedbackPriority;
  title: string;
  content: string;
  position?: {
    x: number;
    y: number;
    width?: number;
    height?: number;
  };
  mentions?: number[];
  tags?: string[];
}

export interface UpdateTimelineFeedbackData extends Partial<CreateTimelineFeedbackData> {
  status?: FeedbackStatus;
}

export interface CreateVideoSessionData {
  video_id: string;
  title: string;
  settings: {
    allow_comments: boolean;
    sync_playback: boolean;
    auto_pause_on_feedback: boolean;
  };
}

export interface CreateRealtimeCommentData {
  session_id: string;
  content: string;
  timestamp?: number;
  mentions?: number[];
  type: 'chat' | 'timestamp';
}

// 피드백 통계
export interface VideoFeedbackStats {
  total_feedbacks: number;
  by_category: Record<FeedbackCategory, number>;
  by_priority: Record<FeedbackPriority, number>;
  by_status: Record<FeedbackStatus, number>;
  most_commented_timestamps: {
    timestamp: number;
    count: number;
  }[];
  resolution_rate: number; // 해결률
}

// WebSocket 메시지 타입들
export interface WebSocketMessage {
  type: 'feedback' | 'comment' | 'playback_sync' | 'user_join' | 'user_leave';
  data: any;
  timestamp: string;
}

export interface PlaybackSyncMessage {
  type: 'playback_sync';
  data: {
    session_id: string;
    current_time: number;
    is_playing: boolean;
    playback_rate: number;
    updated_by: number;
  };
}

export interface NewFeedbackMessage {
  type: 'feedback';
  data: TimelineFeedback;
}

export interface NewCommentMessage {
  type: 'comment';
  data: RealtimeComment;
}