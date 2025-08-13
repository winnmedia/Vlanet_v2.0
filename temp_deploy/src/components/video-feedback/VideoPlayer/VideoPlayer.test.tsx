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
    // Console error/warn을 임시로 비활성화 (테스트 중 불필요한 로그 방지)
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('비디오 플레이어가 올바르게 렌더링된다', () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = screen.getByRole('generic');
    expect(videoElement).toBeInTheDocument();
  });

  it('재생/일시정지 버튼이 작동한다', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    // 재생 버튼 찾기 (초기 상태는 일시정지이므로 재생 버튼이 표시됨)
    const playButton = screen.getByRole('button');
    
    fireEvent.click(playButton);
    
    await waitFor(() => {
      expect(mockPlay).toHaveBeenCalled();
    });
  });

  it('비디오 오류 시 에러 메시지를 표시한다', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    // 비디오 요소 찾기
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // 에러 이벤트 시뮬레이션
      fireEvent.error(videoElement);
      
      await waitFor(() => {
        expect(screen.getByText('재생 오류')).toBeInTheDocument();
        expect(screen.getByText('비디오를 재생할 수 없습니다. 파일을 확인해주세요.')).toBeInTheDocument();
      });
    }
  });

  it('다시 시도 버튼이 에러 상태를 재설정한다', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // 에러 상태 만들기
      fireEvent.error(videoElement);
      
      await waitFor(() => {
        expect(screen.getByText('재생 오류')).toBeInTheDocument();
      });
      
      // 다시 시도 버튼 클릭
      const retryButton = screen.getByText('다시 시도');
      fireEvent.click(retryButton);
      
      await waitFor(() => {
        expect(mockLoad).toHaveBeenCalled();
      });
    }
  });

  it('시간 포맷팅이 올바르게 작동한다', () => {
    render(<VideoPlayer video={mockVideo} />);
    
    // 시간 표시를 찾기 위해 특정 패턴을 사용
    const timeDisplay = screen.getByText(/\d+:\d+/);
    expect(timeDisplay).toBeInTheDocument();
  });

  it('유효하지 않은 시간 값에 대해 안전하게 처리한다', async () => {
    const { rerender } = render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // NaN 값 설정
      Object.defineProperty(videoElement, 'currentTime', {
        writable: true,
        value: NaN
      });
      
      // timeupdate 이벤트 발생
      fireEvent.timeUpdate(videoElement);
      
      // 컴포넌트가 크래시하지 않고 계속 렌더링되는지 확인
      rerender(<VideoPlayer video={mockVideo} />);
      
      // 에러가 발생하지 않았는지 확인
      expect(screen.queryByText('재생 오류')).not.toBeInTheDocument();
    }
  });

  it('메타데이터 로드 시 duration을 올바르게 설정한다', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // duration 설정
      Object.defineProperty(videoElement, 'duration', {
        writable: true,
        value: 120
      });
      
      fireEvent.loadedMetadata(videoElement);
      
      // duration이 설정되었는지 확인 (UI에서 표시되는지)
      await waitFor(() => {
        expect(screen.getByText(/2:00/)).toBeInTheDocument();
      });
    }
  });

  it('무한대 duration 값에 대해 안전하게 처리한다', async () => {
    render(<VideoPlayer video={mockVideo} />);
    
    const videoElement = document.querySelector('video');
    
    if (videoElement) {
      // 무한대 duration 설정
      Object.defineProperty(videoElement, 'duration', {
        writable: true,
        value: Infinity
      });
      
      fireEvent.loadedMetadata(videoElement);
      
      // 에러 메시지가 표시되는지 확인
      await waitFor(() => {
        expect(screen.getByText('비디오 길이를 확인할 수 없습니다.')).toBeInTheDocument();
      });
    }
  });

  it('컴포넌트 언마운트 시 정리 작업을 수행한다', () => {
    const { unmount } = render(<VideoPlayer video={mockVideo} />);
    
    // 언마운트 시 오류가 발생하지 않는지 확인
    expect(() => unmount()).not.toThrow();
  });

  it('콜백 함수들이 올바르게 호출된다', async () => {
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
      // 시간 업데이트 테스트
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

  it('play() 메서드가 실패할 때 에러 처리가 작동한다', async () => {
    // play 메서드가 reject되도록 설정
    mockPlay.mockImplementationOnce(() => Promise.reject(new Error('Play failed')));
    
    render(<VideoPlayer video={mockVideo} />);
    
    const playButton = screen.getByRole('button');
    fireEvent.click(playButton);
    
    await waitFor(() => {
      expect(screen.getByText('비디오 재생에 실패했습니다.')).toBeInTheDocument();
    });
  });
});