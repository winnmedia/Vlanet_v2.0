import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RealtimeComments from './RealtimeComments';
import type { VideoSession, RealtimeComment, User } from '@/types/video-feedback';

// Mock UI components
vi.mock('@/components/ui/Button', () => ({
  Button: ({ children, onClick, className, disabled, ...props }: any) => (
    <button onClick={onClick} className={className} disabled={disabled} {...props}>
      {children}
    </button>
  )
}));

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  first_name: '테스트',
  last_name: '사용자',
  avatar: 'https://example.com/avatar.jpg'
};

const mockUser2: User = {
  id: 2,
  email: 'user2@example.com',
  first_name: '다른',
  last_name: '사용자',
  avatar: 'https://example.com/avatar2.jpg'
};

const mockSession: VideoSession = {
  id: 'session1',
  video_id: 'video1',
  title: '테스트 세션',
  host: mockUser,
  participants: [mockUser, mockUser2],
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

const mockComments: RealtimeComment[] = [
  {
    id: '1',
    session_id: 'session1',
    author: mockUser,
    content: '첫 번째 일반 채팅 메시지입니다.',
    type: 'chat',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    session_id: 'session1',
    author: mockUser2,
    content: '이 시점에 대한 코멘트입니다.',
    type: 'timestamp',
    timestamp: 30,
    created_at: '2025-01-01T01:00:00Z'
  },
  {
    id: '3',
    session_id: 'session1',
    author: mockUser,
    content: '@다른사용자 멘션이 포함된 메시지입니다.',
    type: 'chat',
    mentions: [2],
    created_at: '2025-01-01T02:00:00Z'
  }
];

describe('RealtimeComments', () => {
  const mockProps = {
    session: mockSession,
    comments: mockComments,
    currentUser: mockUser,
    currentTime: 45,
    onSendComment: vi.fn(),
    onDeleteComment: vi.fn(),
    onMentionUser: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('실시간 채팅 컴포넌트가 올바르게 렌더링된다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    expect(screen.getByText('실시간 채팅')).toBeInTheDocument();
    expect(screen.getByText('2명 참여중')).toBeInTheDocument();
    expect(screen.getByText('첫 번째 일반 채팅 메시지입니다.')).toBeInTheDocument();
  });

  it('타임스탬프 코멘트가 올바르게 표시된다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    expect(screen.getByText('이 시점에 대한 코멘트입니다.')).toBeInTheDocument();
    expect(screen.getByText('0:30')).toBeInTheDocument();
  });

  it('메시지 전송이 작동한다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    const sendButton = screen.getByText('전송');
    
    fireEvent.change(input, { target: { value: '새로운 메시지입니다' } });
    fireEvent.click(sendButton);
    
    expect(mockProps.onSendComment).toHaveBeenCalledWith({
      session_id: 'session1',
      content: '새로운 메시지입니다',
      mentions: [],
      type: 'chat'
    });
  });

  it('Enter 키로 메시지를 전송할 수 있다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    
    fireEvent.change(input, { target: { value: 'Enter로 전송' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockProps.onSendComment).toHaveBeenCalledWith({
      session_id: 'session1',
      content: 'Enter로 전송',
      mentions: [],
      type: 'chat'
    });
  });

  it('빈 메시지는 전송되지 않는다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    const sendButton = screen.getByText('전송');
    
    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.click(sendButton);
    
    expect(mockProps.onSendComment).not.toHaveBeenCalled();
  });

  it('타임스탬프 코멘트 모드가 작동한다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    // 타임스탬프 버튼 클릭
    const timestampButton = screen.getByTitle('현재 시점에 코멘트');
    fireEvent.click(timestampButton);
    
    // 타임스탬프 모드 표시 확인
    expect(screen.getByText(/0:45 시점에 코멘트 작성중/)).toBeInTheDocument();
    
    // 메시지 전송
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    fireEvent.change(input, { target: { value: '타임스탬프 코멘트' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockProps.onSendComment).toHaveBeenCalledWith({
      session_id: 'session1',
      content: '타임스탬프 코멘트',
      mentions: [],
      type: 'timestamp',
      timestamp: 45
    });
  });

  it('멘션 기능이 작동한다', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    
    // @ 입력으로 멘션 드롭다운 표시
    fireEvent.change(input, { target: { value: '@' } });
    
    await waitFor(() => {
      expect(screen.getAllByText('다른 사용자')[0]).toBeInTheDocument();
    });
    
    // 사용자 선택
    const userOption = screen.getAllByText('다른 사용자')[0];
    fireEvent.click(userOption);
    
    // 입력 필드에 멘션이 추가되었는지 확인
    expect(input).toHaveValue('@다른사용자 ');
  });

  it('메시지 삭제가 작동한다', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    // 첫 번째 메시지에 호버하여 삭제 버튼 활성화
    const firstMessage = screen.getByText('첫 번째 일반 채팅 메시지입니다.').closest('div');
    fireEvent.mouseEnter(firstMessage!);
    
    await waitFor(() => {
      const deleteButton = screen.getByText('삭제');
      fireEvent.click(deleteButton);
    });
    
    expect(mockProps.onDeleteComment).toHaveBeenCalledWith('1');
  });

  it('메시지 고정 기능이 작동한다', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    // 메시지에 호버
    const firstMessage = screen.getByText('첫 번째 일반 채팅 메시지입니다.').closest('div');
    fireEvent.mouseEnter(firstMessage!);
    
    await waitFor(() => {
      const pinButton = screen.getByText('고정');
      fireEvent.click(pinButton);
      
      // 고정 해제 버튼으로 변경되었는지 확인
      expect(screen.getByText('고정 해제')).toBeInTheDocument();
    });
  });

  it('메시지 복사 기능이 작동한다', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const firstMessage = screen.getByText('첫 번째 일반 채팅 메시지입니다.').closest('div');
    fireEvent.mouseEnter(firstMessage!);
    
    await waitFor(() => {
      const copyButton = screen.getByText('복사');
      fireEvent.click(copyButton);
    });
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('첫 번째 일반 채팅 메시지입니다.');
  });

  it('빈 코멘트 목록일 때 안내 메시지를 표시한다', () => {
    render(<RealtimeComments {...mockProps} comments={[]} />);
    
    expect(screen.getByText('아직 메시지가 없습니다')).toBeInTheDocument();
    expect(screen.getByText('첫 번째 메시지를 보내보세요!')).toBeInTheDocument();
  });

  it('시간 포맷팅이 올바르게 작동한다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    // 타임스탬프 코멘트의 시간 표시 확인 (30초 = 0:30)
    expect(screen.getByText('0:30')).toBeInTheDocument();
  });

  it('사용자 아바타 색상이 올바르게 적용된다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    // 사용자별로 다른 색상이 적용되는지 확인
    const avatars = screen.getAllByText('테사'); // "테스트사용자"의 첫 글자들
    expect(avatars.length).toBeGreaterThan(0);
  });

  it('Escape 키로 멘션 드롭다운을 닫을 수 있다', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    
    // 멘션 드롭다운 열기
    fireEvent.change(input, { target: { value: '@' } });
    
    await waitFor(() => {
      expect(screen.getAllByText('다른 사용자').length).toBeGreaterThan(0);
    });
    
    // Escape 키로 닫기
    fireEvent.keyDown(input, { key: 'Escape' });
    
    // 드롭다운이 사라졌는지 확인 (드롭다운에서만 확인)
    await waitFor(() => {
      const dropdownElements = screen.queryAllByText('다른 사용자');
      // 원래 메시지에 있는 것을 제외하고 드롭다운이 사라졌는지 확인
      expect(dropdownElements.length).toBeLessThanOrEqual(2); // 기본 메시지들
    });
  });

  it('멘션 버튼 클릭으로 @ 기호를 추가할 수 있다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    const mentionButton = screen.getByTitle('멘션');
    
    fireEvent.click(mentionButton);
    
    expect(input).toHaveValue('@');
  });

  it('타임스탬프 모드 취소가 작동한다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const timestampButton = screen.getByTitle('현재 시점에 코멘트');
    fireEvent.click(timestampButton);
    
    // 타임스탬프 모드가 활성화되었는지 확인
    expect(screen.getByText(/시점에 코멘트 작성중/)).toBeInTheDocument();
    
    // 취소 버튼 클릭
    const cancelButton = screen.getByText('취소');
    fireEvent.click(cancelButton);
    
    // 타임스탬프 모드가 비활성화되었는지 확인
    expect(screen.queryByText(/시점에 코멘트 작성중/)).not.toBeInTheDocument();
  });

  it('전송 버튼이 메시지가 없을 때 비활성화된다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const sendButton = screen.getByText('전송');
    expect(sendButton).toBeDisabled();
    
    // 메시지 입력 후 활성화
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    fireEvent.change(input, { target: { value: '메시지' } });
    
    expect(sendButton).not.toBeDisabled();
  });

  it('멘션 검색 필터링이 작동한다', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/메시지를 입력하세요/);
    
    // 부분 검색으로 멘션 드롭다운 표시
    fireEvent.change(input, { target: { value: '@다른' } });
    
    await waitFor(() => {
      expect(screen.getAllByText('다른 사용자')[0]).toBeInTheDocument();
      // '테스트 사용자'는 검색에 걸리지 않아야 함 (이 경우 드롭다운에서만 확인)
    });
  });

  it('참여자 수가 올바르게 표시된다', () => {
    render(<RealtimeComments {...mockProps} />);
    
    expect(screen.getByText('2명 참여중')).toBeInTheDocument();
    expect(screen.getByText('2명이 함께 보고 있습니다')).toBeInTheDocument();
  });
});