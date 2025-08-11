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
  first_name: '',
  last_name: '',
  avatar: 'https://example.com/avatar.jpg'
};

const mockUser2: User = {
  id: 2,
  email: 'user2@example.com',
  first_name: '',
  last_name: '',
  avatar: 'https://example.com/avatar2.jpg'
};

const mockSession: VideoSession = {
  id: 'session1',
  video_id: 'video1',
  title: ' ',
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
    content: '    .',
    type: 'chat',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    session_id: 'session1',
    author: mockUser2,
    content: '   .',
    type: 'timestamp',
    timestamp: 30,
    created_at: '2025-01-01T01:00:00Z'
  },
  {
    id: '3',
    session_id: 'session1',
    author: mockUser,
    content: '@   .',
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

  it('    ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    expect(screen.getByText(' ')).toBeInTheDocument();
    expect(screen.getByText('2 ')).toBeInTheDocument();
    expect(screen.getByText('    .')).toBeInTheDocument();
  });

  it('   ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    expect(screen.getByText('   .')).toBeInTheDocument();
    expect(screen.getByText('0:30')).toBeInTheDocument();
  });

  it('  ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    const sendButton = screen.getByText('');
    
    fireEvent.change(input, { target: { value: ' ' } });
    fireEvent.click(sendButton);
    
    expect(mockProps.onSendComment).toHaveBeenCalledWith({
      session_id: 'session1',
      content: ' ',
      mentions: [],
      type: 'chat'
    });
  });

  it('Enter     ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    
    fireEvent.change(input, { target: { value: 'Enter ' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockProps.onSendComment).toHaveBeenCalledWith({
      session_id: 'session1',
      content: 'Enter ',
      mentions: [],
      type: 'chat'
    });
  });

  it('   ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    const sendButton = screen.getByText('');
    
    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.click(sendButton);
    
    expect(mockProps.onSendComment).not.toHaveBeenCalled();
  });

  it('   ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    //   
    const timestampButton = screen.getByTitle('  ');
    fireEvent.click(timestampButton);
    
    //    
    expect(screen.getByText(/0:45   /)).toBeInTheDocument();
    
    //  
    const input = screen.getByPlaceholderText(/ /);
    fireEvent.change(input, { target: { value: ' ' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockProps.onSendComment).toHaveBeenCalledWith({
      session_id: 'session1',
      content: ' ',
      mentions: [],
      type: 'timestamp',
      timestamp: 45
    });
  });

  it('  ', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    
    // @    
    fireEvent.change(input, { target: { value: '@' } });
    
    await waitFor(() => {
      expect(screen.getAllByText(' ')[0]).toBeInTheDocument();
    });
    
    //  
    const userOption = screen.getAllByText(' ')[0];
    fireEvent.click(userOption);
    
    //     
    expect(input).toHaveValue('@ ');
  });

  it('  ', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    //       
    const firstMessage = screen.getByText('    .').closest('div');
    fireEvent.mouseEnter(firstMessage!);
    
    await waitFor(() => {
      const deleteButton = screen.getByText('');
      fireEvent.click(deleteButton);
    });
    
    expect(mockProps.onDeleteComment).toHaveBeenCalledWith('1');
  });

  it('   ', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    //  
    const firstMessage = screen.getByText('    .').closest('div');
    fireEvent.mouseEnter(firstMessage!);
    
    await waitFor(() => {
      const pinButton = screen.getByText('');
      fireEvent.click(pinButton);
      
      //     
      expect(screen.getByText(' ')).toBeInTheDocument();
    });
  });

  it('   ', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const firstMessage = screen.getByText('    .').closest('div');
    fireEvent.mouseEnter(firstMessage!);
    
    await waitFor(() => {
      const copyButton = screen.getByText('');
      fireEvent.click(copyButton);
    });
    
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('    .');
  });

  it('      ', () => {
    render(<RealtimeComments {...mockProps} comments={[]} />);
    
    expect(screen.getByText('  ')).toBeInTheDocument();
    expect(screen.getByText('   !')).toBeInTheDocument();
  });

  it('   ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    //      (30 = 0:30)
    expect(screen.getByText('0:30')).toBeInTheDocument();
  });

  it('    ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    //     
    const avatars = screen.getAllByText(''); // ""  
    expect(avatars.length).toBeGreaterThan(0);
  });

  it('Escape      ', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    
    //   
    fireEvent.change(input, { target: { value: '@' } });
    
    await waitFor(() => {
      expect(screen.getAllByText(' ').length).toBeGreaterThan(0);
    });
    
    // Escape  
    fireEvent.keyDown(input, { key: 'Escape' });
    
    //    ( )
    await waitFor(() => {
      const dropdownElements = screen.queryAllByText(' ');
      //        
      expect(dropdownElements.length).toBeLessThanOrEqual(2); //  
    });
  });

  it('   @    ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    const mentionButton = screen.getByTitle('');
    
    fireEvent.click(mentionButton);
    
    expect(input).toHaveValue('@');
  });

  it('   ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const timestampButton = screen.getByTitle('  ');
    fireEvent.click(timestampButton);
    
    //    
    expect(screen.getByText(/  /)).toBeInTheDocument();
    
    //   
    const cancelButton = screen.getByText('');
    fireEvent.click(cancelButton);
    
    //    
    expect(screen.queryByText(/  /)).not.toBeInTheDocument();
  });

  it('     ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    const sendButton = screen.getByText('');
    expect(sendButton).toBeDisabled();
    
    //    
    const input = screen.getByPlaceholderText(/ /);
    fireEvent.change(input, { target: { value: '' } });
    
    expect(sendButton).not.toBeDisabled();
  });

  it('   ', async () => {
    render(<RealtimeComments {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ /);
    
    //     
    fireEvent.change(input, { target: { value: '@' } });
    
    await waitFor(() => {
      expect(screen.getAllByText(' ')[0]).toBeInTheDocument();
      // ' '     (   )
    });
  });

  it('   ', () => {
    render(<RealtimeComments {...mockProps} />);
    
    expect(screen.getByText('2 ')).toBeInTheDocument();
    expect(screen.getByText('2   ')).toBeInTheDocument();
  });
});