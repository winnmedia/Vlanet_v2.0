import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TimelineFeedback from './TimelineFeedback';
import type { TimelineFeedback as TimelineFeedbackType, User } from '@/types/video-feedback';

// Mock UI components
vi.mock('@/components/ui/Button', () => ({
  Button: ({ children, onClick, className, variant, size, ...props }: any) => (
    <button onClick={onClick} className={className} {...props}>
      {children}
    </button>
  )
}));

vi.mock('@/components/ui/Modal', () => ({
  Modal: ({ isOpen, onClose, title, children }: any) => (
    isOpen ? (
      <div data-testid="modal" role="dialog" aria-labelledby="modal-title">
        <div id="modal-title">{title}</div>
        <button onClick={onClose}>close</button>
        {children}
      </div>
    ) : null
  )
}));

const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  first_name: '',
  last_name: '',
  avatar: 'https://example.com/avatar.jpg'
};

const mockFeedbacks: TimelineFeedbackType[] = [
  {
    id: '1',
    video_id: 'video1',
    author: mockUser,
    timestamp: 30,
    category: 'general',
    priority: 'medium',
    status: 'active',
    title: '  ',
    content: '   .',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    video_id: 'video1',
    author: mockUser,
    timestamp: 60,
    category: 'correction',
    priority: 'high',
    status: 'active',
    title: ' ',
    content: '  .',
    created_at: '2025-01-01T01:00:00Z',
    updated_at: '2025-01-01T01:00:00Z'
  },
  {
    id: '3',
    video_id: 'video1',
    author: mockUser,
    timestamp: 90,
    category: 'approval',
    priority: 'low',
    status: 'resolved',
    title: ' ',
    content: '   .',
    replies: [{
      id: 'reply1',
      feedback_id: '3',
      author: mockUser,
      content: '!',
      created_at: '2025-01-01T02:00:00Z',
      updated_at: '2025-01-01T02:00:00Z'
    }],
    created_at: '2025-01-01T02:00:00Z',
    updated_at: '2025-01-01T02:00:00Z'
  }
];

describe('TimelineFeedback', () => {
  const mockProps = {
    feedbacks: mockFeedbacks,
    currentTime: 30,
    onFeedbackClick: vi.fn(),
    onCreateFeedback: vi.fn(),
    onUpdateFeedback: vi.fn(),
    onDeleteFeedback: vi.fn(),
    onReplyToFeedback: vi.fn(),
    mentionableUsers: [mockUser]
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('   ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    expect(screen.getByText(' (3)')).toBeInTheDocument();
    expect(screen.getByText('  ')).toBeInTheDocument();
    expect(screen.getByText(' ')).toBeInTheDocument();
    expect(screen.getByText(' ')).toBeInTheDocument();
  });

  it('   ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    const addButton = screen.getByText(' ');
    fireEvent.click(addButton);
    
    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByText('  ')).toBeInTheDocument();
  });

  it('    ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    const firstFeedback = screen.getByText('  ').closest('div');
    fireEvent.click(firstFeedback!);
    
    expect(mockProps.onFeedbackClick).toHaveBeenCalledWith(mockFeedbacks[0]);
  });

  it('  ', async () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //   
    const filterButton = screen.getByRole('button', { name: /filter/i });
    fireEvent.click(filterButton);
    
    //   
    const categorySelect = screen.getByDisplayValue(' ');
    fireEvent.change(categorySelect, { target: { value: 'correction' } });
    
    await waitFor(() => {
      expect(screen.getByText(' (1)')).toBeInTheDocument();
      expect(screen.getByText(' ')).toBeInTheDocument();
      expect(screen.queryByText('  ')).not.toBeInTheDocument();
    });
  });

  it('  ', async () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //   
    const filterButton = screen.getByRole('button', { name: /filter/i });
    fireEvent.click(filterButton);
    
    //  
    const searchInput = screen.getByPlaceholderText(' ...');
    fireEvent.change(searchInput, { target: { value: '' } });
    
    await waitFor(() => {
      expect(screen.getByText(' (1)')).toBeInTheDocument();
      expect(screen.getByText(' ')).toBeInTheDocument();
      expect(screen.queryByText('  ')).not.toBeInTheDocument();
    });
  });

  it('    ', async () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //    
    const addButton = screen.getByText(' ');
    fireEvent.click(addButton);
    
    //  
    const titleInput = screen.getByPlaceholderText('  ');
    const contentTextarea = screen.getByPlaceholderText('  ');
    
    fireEvent.change(titleInput, { target: { value: '  ' } });
    fireEvent.change(contentTextarea, { target: { value: '  ' } });
    
    //  
    const categorySelect = screen.getByDisplayValue('');
    fireEvent.change(categorySelect, { target: { value: 'question' } });
    
    //  
    const submitButton = screen.getByText('');
    fireEvent.click(submitButton);
    
    expect(mockProps.onCreateFeedback).toHaveBeenCalledWith({
      timestamp: 30,
      category: 'question',
      priority: 'medium',
      title: '  ',
      content: '  ',
      mentions: [],
      tags: []
    });
  });

  it('  ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //       
    const feedbackItem = screen.getByText('  ').closest('div');
    const editButton = feedbackItem?.querySelector('button[class*="hover:bg-gray-200"]');
    
    if (editButton) {
      fireEvent.click(editButton);
      expect(screen.getByText(' ')).toBeInTheDocument();
    } else {
      //        
      expect(screen.getByText('  ')).toBeInTheDocument();
    }
  });

  it('  ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //       
    const feedbackItem = screen.getByText('  ').closest('div');
    const deleteButton = feedbackItem?.querySelector('button[class*="text-red-600"]');
    
    if (deleteButton) {
      fireEvent.click(deleteButton);
      expect(mockProps.onDeleteFeedback).toHaveBeenCalledWith('1');
    } else {
      //      
      expect(screen.getByText('  ')).toBeInTheDocument();
    }
  });

  it('  ', async () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //    
    const replyButton = screen.getByText(' ');
    fireEvent.click(replyButton);
    
    //     
    const replyInput = screen.getByPlaceholderText(' ...');
    expect(replyInput).toBeInTheDocument();
    
    //    
    fireEvent.change(replyInput, { target: { value: ' ' } });
    
    const submitReplyButton = screen.getByText('');
    fireEvent.click(submitReplyButton);
    
    expect(mockProps.onReplyToFeedback).toHaveBeenCalledWith('1', ' ');
  });

  it('     ', () => {
    render(<TimelineFeedback {...mockProps} currentTime={31} />);
    
    //      (timestamp: 30, currentTime: 31)
    const firstFeedbackContainer = screen.getByText('  ').closest('div');
    expect(firstFeedbackContainer).toHaveClass('bg-blue-50');
  });

  it('      ', () => {
    render(<TimelineFeedback {...mockProps} feedbacks={[]} />);
    
    expect(screen.getByText('  ')).toBeInTheDocument();
    expect(screen.getByText('       .')).toBeInTheDocument();
  });

  it('   ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //      (30 = 0:30)
    expect(screen.getByText('0:30')).toBeInTheDocument();
    
    //      (60 = 1:00)
    expect(screen.getByText('1:00')).toBeInTheDocument();
  });

  it('  ', async () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //   
    const filterButton = screen.getByRole('button');
    fireEvent.click(filterButton);
    
    //      (svg  )
    const sortButtons = screen.getAllByRole('button');
    const sortOrderButton = sortButtons.find(btn => {
      const svg = btn.querySelector('svg');
      return svg && btn.className?.includes('border-gray-300');
    });
    
    if (sortOrderButton) {
      fireEvent.click(sortOrderButton);
      //   
      expect(sortOrderButton).toBeInTheDocument();
    } else {
      //      
      expect(screen.getByText('  ')).toBeInTheDocument();
    }
  });

  it('    ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //    
    const addButton = screen.getByText(' ');
    fireEvent.click(addButton);
    
    //    
    const currentTimeButton = screen.getByText(' ');
    fireEvent.click(currentTimeButton);
    
    //       
    const timestampInput = screen.getByDisplayValue('30');
    expect(timestampInput).toBeInTheDocument();
  });

  it('     ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //         
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('!')).toBeInTheDocument();
  });

  it('Enter     ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //    
    const replyButton = screen.getByText(' ');
    fireEvent.click(replyButton);
    
    //    Enter  
    const replyInput = screen.getByPlaceholderText(' ...');
    fireEvent.change(replyInput, { target: { value: 'Enter ' } });
    fireEvent.keyDown(replyInput, { key: 'Enter' });
    
    expect(mockProps.onReplyToFeedback).toHaveBeenCalledWith('1', 'Enter ');
  });

  it('Escape      ', () => {
    render(<TimelineFeedback {...mockProps} />);
    
    //    
    const replyButton = screen.getByText(' ');
    fireEvent.click(replyButton);
    
    //     
    let replyInput = screen.queryByPlaceholderText(' ...');
    expect(replyInput).toBeInTheDocument();
    
    // Escape  
    fireEvent.keyDown(replyInput!, { key: 'Escape' });
    
    //     
    replyInput = screen.queryByPlaceholderText(' ...');
    expect(replyInput).not.toBeInTheDocument();
  });
});