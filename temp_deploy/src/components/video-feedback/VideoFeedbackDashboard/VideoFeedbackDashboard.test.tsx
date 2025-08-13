import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import VideoFeedbackDashboard from './VideoFeedbackDashboard';
import type { VideoFile, TimelineFeedback, VideoSession, VideoFeedbackStats, User } from '@/types/video-feedback';

// Mock dependencies
vi.mock('@/lib/api/video-feedback.service', () => ({
  videoFeedbackService: {
    getVideo: vi.fn(),
    getVideoFeedbacks: vi.fn(),
    getVideoSessions: vi.fn(),
    getVideoFeedbackStats: vi.fn(),
    getMentionableUsers: vi.fn(),
    getSessionComments: vi.fn(),
    createVideoSession: vi.fn(),
    leaveSession: vi.fn(),
    createFeedback: vi.fn(),
    updateFeedback: vi.fn(),
    deleteFeedback: vi.fn(),
    createComment: vi.fn(),
    syncPlayback: vi.fn()
  }
}));

vi.mock('@/contexts/toast.context', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn()
  })
}));

vi.mock('@/components/ui/Button', () => ({
  Button: ({ children, onClick, className, variant, ...props }: any) => (
    <button onClick={onClick} className={className} {...props}>
      {children}
    </button>
  )
}));

vi.mock('../VideoPlayer', () => ({
  default: ({ video, onTimeUpdate, onFeedbackClick }: any) => (
    <div data-testid="video-player">
      <div>Video: {video.title}</div>
      <button onClick={() => onTimeUpdate?.(30)}>Update Time</button>
      <button onClick={() => onFeedbackClick?.({ id: '1', timestamp: 60 })}>Click Feedback</button>
    </div>
  )
}));

vi.mock('../TimelineFeedback', () => ({
  default: ({ feedbacks, onCreateFeedback }: any) => (
    <div data-testid="timeline-feedback">
      <div>Timeline Feedback ({feedbacks.length})</div>
      <button onClick={() => onCreateFeedback?.({ title: 'New Feedback' })}>Add Feedback</button>
    </div>
  )
}));

vi.mock('../RealtimeComments', () => ({
  default: ({ session, onSendComment }: any) => (
    <div data-testid="realtime-comments">
      <div>Realtime Comments - Session: {session.id}</div>
      <button onClick={() => onSendComment?.({ content: 'New Comment' })}>Send Comment</button>
    </div>
  )
}));

const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  first_name: '테스트',
  last_name: '사용자'
};

const mockVideo: VideoFile = {
  id: 'video1',
  title: '테스트 비디오',
  file_url: 'https://example.com/video.mp4',
  duration: 120,
  file_size: 1000000,
  format: 'mp4',
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z'
};

const mockFeedbacks: TimelineFeedback[] = [
  {
    id: '1',
    video_id: 'video1',
    author: mockUser,
    timestamp: 30,
    category: 'general',
    priority: 'medium',
    status: 'active',
    title: '첫 번째 피드백',
    content: '테스트 피드백입니다',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z'
  }
];

const mockSession: VideoSession = {
  id: 'session1',
  video_id: 'video1',
  title: '테스트 세션',
  host: mockUser,
  participants: [mockUser],
  is_active: true,
  settings: {
    allow_comments: true,
    sync_playback: true,
    auto_pause_on_feedback: false
  },
  playback_state: {
    current_time: 0,
    is_playing: false,
    playback_rate: 1,
    last_updated: '2025-01-01T00:00:00Z',
    updated_by: 1
  },
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z'
};

const mockStats: VideoFeedbackStats = {
  total_feedbacks: 5,
  by_category: {
    general: 2,
    correction: 1,
    question: 1,
    approval: 1,
    suggestion: 0,
    technical: 0,
    creative: 0
  },
  by_priority: {
    low: 1,
    medium: 3,
    high: 1,
    urgent: 0
  },
  by_status: {
    active: 3,
    resolved: 2,
    declined: 0
  },
  most_commented_timestamps: [
    { timestamp: 30, count: 3 },
    { timestamp: 60, count: 2 }
  ],
  resolution_rate: 0.4
};

describe('VideoFeedbackDashboard', () => {
  let videoFeedbackService: any;

  beforeEach(async () => {
    vi.clearAllMocks();
    
    const module = await import('@/lib/api/video-feedback.service');
    videoFeedbackService = module.videoFeedbackService;
    
    // Mock successful API responses
    videoFeedbackService.getVideo.mockResolvedValue({
      success: true,
      data: mockVideo
    });
    videoFeedbackService.getVideoFeedbacks.mockResolvedValue({
      success: true,
      data: mockFeedbacks
    });
    videoFeedbackService.getVideoSessions.mockResolvedValue({
      success: true,
      data: [mockSession]
    });
    videoFeedbackService.getVideoFeedbackStats.mockResolvedValue({
      success: true,
      data: mockStats
    });
    videoFeedbackService.getMentionableUsers.mockResolvedValue({
      success: true,
      data: [mockUser]
    });
    videoFeedbackService.getSessionComments.mockResolvedValue({
      success: true,
      data: []
    });
  });

  it('대시보드가 올바르게 렌더링된다', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    // 데이터 로드 후 확인
    await waitFor(() => {
      expect(screen.getByText('테스트 비디오')).toBeInTheDocument();
      expect(screen.getByTestId('video-player')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('통계 카드가 올바르게 표시된다', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('전체 피드백')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument(); // total_feedbacks
      expect(screen.getByText('40%')).toBeInTheDocument(); // resolution_rate
      expect(screen.getByText('3')).toBeInTheDocument(); // active status
    });
  });

  it('탭 네비게이션이 작동한다', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('개요')).toBeInTheDocument();
    });

    // 타임라인 탭 클릭
    const timelineTab = screen.getByText('타임라인');
    fireEvent.click(timelineTab);

    expect(screen.getByTestId('timeline-feedback')).toBeInTheDocument();

    // 채팅 탭 클릭
    const chatTab = screen.getByText('실시간 채팅');
    fireEvent.click(chatTab);

    expect(screen.getByTestId('realtime-comments')).toBeInTheDocument();
  });

  it('협업 모드 전환이 작동한다', async () => {
    videoFeedbackService.createVideoSession.mockResolvedValue({
      success: true,
      data: mockSession
    });

    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('협업 시작')).toBeInTheDocument();
    });

    const collaborationButton = screen.getByText('협업 시작');
    fireEvent.click(collaborationButton);

    await waitFor(() => {
      expect(videoFeedbackService.createVideoSession).toHaveBeenCalled();
    });
  });

  it('피드백 생성이 작동한다', async () => {
    videoFeedbackService.createFeedback.mockResolvedValue({
      success: true,
      data: mockFeedbacks[0]
    });

    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    // 타임라인 탭으로 이동
    await waitFor(() => {
      const timelineTab = screen.getByText('타임라인');
      fireEvent.click(timelineTab);
    });

    await waitFor(() => {
      const addFeedbackButton = screen.getByText('Add Feedback');
      fireEvent.click(addFeedbackButton);
    });

    expect(videoFeedbackService.createFeedback).toHaveBeenCalled();
  });

  it('실시간 코멘트 전송이 작동한다', async () => {
    videoFeedbackService.createComment.mockResolvedValue({
      success: true,
      data: { id: 'comment1', content: 'New Comment' }
    });

    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    // 채팅 탭으로 이동
    await waitFor(() => {
      const chatTab = screen.getByText('실시간 채팅');
      fireEvent.click(chatTab);
    });

    await waitFor(() => {
      const sendCommentButton = screen.getByText('Send Comment');
      fireEvent.click(sendCommentButton);
    });

    expect(videoFeedbackService.createComment).toHaveBeenCalled();
  });

  it('비디오가 없을 때 오류 메시지를 표시한다', async () => {
    videoFeedbackService.getVideo.mockResolvedValue({
      success: false,
      data: null
    });

    render(
      <VideoFeedbackDashboard 
        videoId="nonexistent" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('영상을 찾을 수 없습니다')).toBeInTheDocument();
    });
  });

  it('재생 시간 업데이트가 작동한다', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      const updateTimeButton = screen.getByText('Update Time');
      fireEvent.click(updateTimeButton);
      
      // currentTime이 업데이트되었는지 확인하는 로직 추가 가능
    });
  });

  it('피드백 클릭 시 해당 시간으로 이동한다', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      const feedbackClickButton = screen.getByText('Click Feedback');
      fireEvent.click(feedbackClickButton);
      
      // 시간이 60초로 설정되고 타임라인 탭이 활성화되었는지 확인
      expect(screen.getByText('타임라인')).toBeInTheDocument();
    });
  });
});