import React from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import VideoPlayer from './VideoPlayer';
import type { VideoFile } from '@/types/video-feedback';

// HTMLMediaElement mock
const mockPlay = vi.fn();
const mockPause = vi.fn();
const mockLoad = vi.fn();

Object.defineProperty(HTMLMediaElement.prototype, 'play', {
  writable: true,
  value: mockPlay.mockImplementation(() => Promise.resolve())
});

Object.defineProperty(HTMLMediaElement.prototype, 'pause', {
  writable: true,
  value: mockPause
});

Object.defineProperty(HTMLMediaElement.prototype, 'load', {
  writable: true,
  value: mockLoad
});

Object.defineProperty(HTMLMediaElement.prototype, 'currentTime', {
  writable: true,
  value: 0
});

Object.defineProperty(HTMLMediaElement.prototype, 'duration', {
  writable: true,
  value: 100
});

const mockVideo: VideoFile = {
  id: '1',
  title: 'Test Video',
  file_url: 'https://example.com/video.mp4',
  thumbnail_url: 'https://example.com/thumb.jpg',
  duration: 120,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z'
};

describe('VideoPlayer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Console error/warn   (    )
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('   ', () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = screen.getByRole('generic');
    expect(videoElement).toBeInTheDocument();
  });

  it('/  ', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    //    (     )
    const playButton = screen.getByRole('button');
    
    fireEvent.click(playButton);
    
    await waitFor(() => {
      expect(mockPlay).toHaveBeenCalled();
    });
  });

  it('     ', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    //   
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      //   
      fireEvent.error(videoElement);
      
      await waitFor(() => {
        expect(screen.getByText(' ')).toBeInTheDocument();
        expect(screen.getByText('   .  .')).toBeInTheDocument();
      });
    }
  });

  it('     ', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      //   
      fireEvent.error(videoElement);
      
      await waitFor(() => {
        expect(screen.getByText(' ')).toBeInTheDocument();
      });
      
      //    
      const retryButton = screen.getByText(' ');
      fireEvent.click(retryButton);
      
      await waitFor(() => {
        expect(mockLoad).toHaveBeenCalled();
      });
    }
  });

  it('   ', () => {
    render(<VideoPlayer video={mockVideo} />);
    
    //       
    const timeDisplay = screen.getByText(/\d+:\d+/);
    expect(timeDisplay).toBeInTheDocument();
  });

  it('      ', async () => {
    const { rerender } = render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // NaN  
      Object.defineProperty(videoElement, 'currentTime', {
        writable: true,
        value: NaN
      });
      
      // timeupdate  
      fireEvent.timeUpdate(videoElement);
      
      //      
      rerender(<VideoPlayer video={mockVideo} />);
      
      //    
      expect(screen.queryByText(' ')).not.toBeInTheDocument();
    }
  });

  it('   duration  ', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // duration 
      Object.defineProperty(videoElement, 'duration', {
        writable: true,
        value: 120
      });
      
      fireEvent.loadedMetadata(videoElement);
      
      // duration   (UI )
      await waitFor(() => {
        expect(screen.getByText(/2:00/)).toBeInTheDocument();
      });
    }
  });

  it(' duration    ', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      //  duration 
      Object.defineProperty(videoElement, 'duration', {
        writable: true,
        value: Infinity
      });
      
      fireEvent.loadedMetadata(videoElement);
      
      //    
      await waitFor(() => {
        expect(screen.getByText('    .')).toBeInTheDocument();
      });
    }
  });

  it('     ', () => {
    const { unmount } = render(<VideoPlayer video={mockVideo} />);
    
    //      
    expect(() => unmount()).not.toThrow();
  });

  it('   ', async () => {
    const onTimeUpdate = vi.fn();
    const onFeedbackClick = vi.fn();
    const onAddFeedback = vi.fn();
    const onPlaybackSync = vi.fn();
    
    render(
      <VideoPlayer 
        video={mockVideo}
        onTimeUpdate={onTimeUpdate}
        onFeedbackClick={onFeedbackClick}
        onAddFeedback={onAddFeedback}
        onPlaybackSync={onPlaybackSync}
        syncEnabled={true}
      />
    );
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      //   
      Object.defineProperty(videoElement, 'currentTime', {
        writable: true,
        value: 30
      });
      
      fireEvent.timeUpdate(videoElement);
      
      await waitFor(() => {
        expect(onTimeUpdate).toHaveBeenCalledWith(30);
      });
    }
  });

  it('play()      ', async () => {
    // play  reject 
    mockPlay.mockImplementationOnce(() => Promise.reject(new Error('Play failed')));
    
    render(<VideoPlayer video={mockVideo} />);
    
    const playButton = screen.getByRole('button');
    fireEvent.click(playButton);
    
    await waitFor(() => {
      expect(screen.getByText('  .')).toBeInTheDocument();
    });
  });
});