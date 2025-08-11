/**
 *     
 *        
 */

//  
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  avatar?: string;
}

//   
export interface VideoFile {
  id: string;
  title: string;
  description?: string;
  file_url: string;
  thumbnail_url?: string;
  duration: number; //  
  resolution?: string;
  file_size: number;
  format: string;
  project_id?: number;
  created_at: string;
  updated_at: string;
}

//    
export type FeedbackCategory = 
  | 'general'        // 
  | 'correction'     // 
  | 'question'       // 
  | 'approval'       // 
  | 'suggestion'     // 
  | 'technical'      //  
  | 'creative';      //  

export type FeedbackPriority = 'low' | 'medium' | 'high' | 'urgent';

export type FeedbackStatus = 'active' | 'resolved' | 'declined';

//    (   )
export interface TimelineFeedback {
  id: string;
  video_id: string;
  author: User;
  timestamp: number; //   ( )
  category: FeedbackCategory;
  priority: FeedbackPriority;
  status: FeedbackStatus;
  
  //  
  title: string;
  content: string;
  
  //   ( -   )
  position?: {
    x: number; //   X  (0-1 )
    y: number; //   Y  (0-1 )
    width?: number;
    height?: number;
  };
  
  // 
  attachments?: {
    id: string;
    filename: string;
    url: string;
    type: 'image' | 'document' | 'audio';
  }[];
  
  // 
  replies?: TimelineFeedbackReply[];
  
  // 
  mentions?: number[]; //   ID
  tags?: string[];
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  resolved_by?: User;
}

//   
export interface TimelineFeedbackReply {
  id: string;
  feedback_id: string;
  author: User;
  content: string;
  mentions?: number[];
  created_at: string;
  updated_at: string;
}

//   (    )
export interface VideoSession {
  id: string;
  video_id: string;
  title: string;
  host: User;
  participants: User[];
  is_active: boolean;
  
  //  
  settings: {
    allow_comments: boolean;
    sync_playback: boolean; //  
    auto_pause_on_feedback: boolean; //     
  };
  
  //    ()
  playback_state: {
    current_time: number;
    is_playing: boolean;
    playback_rate: number;
    last_updated: string;
    updated_by: number; //  ID
  };
  
  created_at: string;
  updated_at: string;
}

//   ( )
export interface RealtimeComment {
  id: string;
  session_id: string;
  author: User;
  content: string;
  timestamp?: number; //   ()
  mentions?: number[];
  type: 'chat' | 'timestamp'; //     
  created_at: string;
}

//   ( / )
export interface FeedbackFrame {
  id: string;
  video_id: string;
  timestamp: number;
  frame_url: string; //  URL
  annotations?: {
    id: string;
    type: 'arrow' | 'circle' | 'rectangle' | 'text';
    position: { x: number; y: number; width?: number; height?: number };
    color: string;
    content?: string;
  }[];
  created_at: string;
}

// API / 
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

//  
export interface VideoFeedbackStats {
  total_feedbacks: number;
  by_category: Record<FeedbackCategory, number>;
  by_priority: Record<FeedbackPriority, number>;
  by_status: Record<FeedbackStatus, number>;
  most_commented_timestamps: {
    timestamp: number;
    count: number;
  }[];
  resolution_rate: number; // 
}

// WebSocket  
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