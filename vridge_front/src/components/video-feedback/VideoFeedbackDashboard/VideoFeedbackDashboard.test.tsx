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
  first_name: '',
  last_name: ''
};

const mockVideo: VideoFile = {
  id: 'video1',
  title: ' ',
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
    title: '  ',
    content: ' ',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z'
  }
];

const mockSession: VideoSession = {
  id: 'session1',
  video_id: 'video1',
  title: ' ',
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

  it('  ', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    //    
    await waitFor(() => {
      expect(screen.getByText(' ')).toBeInTheDocument();
      expect(screen.getByTestId('video-player')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('   ', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(' ')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument(); // total_feedbacks
      expect(screen.getByText('40%')).toBeInTheDocument(); // resolution_rate
      expect(screen.getByText('3')).toBeInTheDocument(); // active status
    });
  });

  it('  ', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('')).toBeInTheDocument();
    });

    //   
    const timelineTab = screen.getByText('');
    fireEvent.click(timelineTab);

    expect(screen.getByTestId('timeline-feedback')).toBeInTheDocument();

    //   
    const chatTab = screen.getByText(' ');
    fireEvent.click(chatTab);

    expect(screen.getByTestId('realtime-comments')).toBeInTheDocument();
  });

  it('   ', async () => {
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
      expect(screen.getByText(' ')).toBeInTheDocument();
    });

    const collaborationButton = screen.getByText(' ');
    fireEvent.click(collaborationButton);

    await waitFor(() => {
      expect(videoFeedbackService.createVideoSession).toHaveBeenCalled();
    });
  });

  it('  ', async () => {
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

    //   
    await waitFor(() => {
      const timelineTab = screen.getByText('');
      fireEvent.click(timelineTab);
    });

    await waitFor(() => {
      const addFeedbackButton = screen.getByText('Add Feedback');
      fireEvent.click(addFeedbackButton);
    });

    expect(videoFeedbackService.createFeedback).toHaveBeenCalled();
  });

  it('   ', async () => {
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

    //   
    await waitFor(() => {
      const chatTab = screen.getByText(' ');
      fireEvent.click(chatTab);
    });

    await waitFor(() => {
      const sendCommentButton = screen.getByText('Send Comment');
      fireEvent.click(sendCommentButton);
    });

    expect(videoFeedbackService.createComment).toHaveBeenCalled();
  });

  it('     ', async () => {
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
      expect(screen.getByText('   ')).toBeInTheDocument();
    });
  });

  it('   ', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      const updateTimeButton = screen.getByText('Update Time');
      fireEvent.click(updateTimeButton);
      
      // currentTime     
    });
  });

  it('     ', async () => {
    render(
      <VideoFeedbackDashboard 
        videoId="video1" 
        currentUser={mockUser}
      />
    );

    await waitFor(() => {
      const feedbackClickButton = screen.getByText('Click Feedback');
      fireEvent.click(feedbackClickButton);
      
      //  60     
      expect(screen.getByText('')).toBeInTheDocument();
    });
  });
});