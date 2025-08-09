'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize, 
  Settings, 
  RotateCcw,
  RotateCw,
  MessageSquare,
  Plus
} from 'lucide-react';
import type { VideoFile, TimelineFeedback, VideoSession } from '@/types/video-feedback';

interface VideoPlayerProps {
  video: VideoFile;
  feedbacks?: TimelineFeedback[];
  session?: VideoSession;
  onTimeUpdate?: (currentTime: number) => void;
  onFeedbackClick?: (feedback: TimelineFeedback) => void;
  onAddFeedback?: (timestamp: number, position?: { x: number; y: number }) => void;
  onPlaybackSync?: (state: { currentTime: number; isPlaying: boolean; playbackRate: number }) => void;
  syncEnabled?: boolean;
  showFeedbackMarkers?: boolean;
  allowNewFeedbacks?: boolean;
  className?: string;
}

interface PlaybackState {
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  isLoading: boolean;
  volume: number;
  playbackRate: number;
  isFullscreen: boolean;
  isMuted: boolean;
}

export default function VideoPlayer({
  video,
  feedbacks = [],
  session,
  onTimeUpdate,
  onFeedbackClick,
  onAddFeedback,
  onPlaybackSync,
  syncEnabled = false,
  showFeedbackMarkers = true,
  allowNewFeedbacks = true,
  className = ''
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const isMountedRef = useRef<boolean>(true);
  
  const [state, setState] = useState<PlaybackState>({
    currentTime: 0,
    duration: 0,
    isPlaying: false,
    isLoading: true,
    volume: 1,
    playbackRate: 1,
    isFullscreen: false,
    isMuted: false
  });

  const [showControls, setShowControls] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [hoveredFeedback, setHoveredFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 컨트롤 자동 숨김 타이머
  const hideControlsTimeout = useRef<NodeJS.Timeout>();

  // 안전한 상태 업데이트 함수
  const safeSetState = useCallback((updater: (prev: PlaybackState) => PlaybackState) => {
    if (isMountedRef.current) {
      setState(updater);
    }
  }, []);

  const resetHideTimer = useCallback(() => {
    if (hideControlsTimeout.current) {
      clearTimeout(hideControlsTimeout.current);
    }
    setShowControls(true);
    hideControlsTimeout.current = setTimeout(() => {
      if (state.isPlaying) {
        setShowControls(false);
      }
    }, 3000);
  }, [state.isPlaying]);

  // 비디오 이벤트 핸들러 (안전성 강화)
  const handleLoadedMetadata = useCallback(() => {
    try {
      if (videoRef.current && isMountedRef.current) {
        const duration = videoRef.current.duration;
        // NaN 또는 무한대 값 검증
        if (isFinite(duration) && duration > 0) {
          safeSetState(prev => ({
            ...prev,
            duration,
            isLoading: false
          }));
          setError(null);
        } else {
          setError('비디오 길이를 확인할 수 없습니다.');
        }
      }
    } catch (err) {
      console.error('[VideoPlayer] 메타데이터 로드 오류:', err);
      setError('비디오 메타데이터 로드 중 오류가 발생했습니다.');
    }
  }, [safeSetState]);

  const handleTimeUpdate = useCallback(() => {
    try {
      if (videoRef.current && !isDragging && isMountedRef.current) {
        const currentTime = videoRef.current.currentTime;
        if (isFinite(currentTime) && currentTime >= 0) {
          safeSetState(prev => ({ ...prev, currentTime }));
          onTimeUpdate?.(currentTime);
        }
      }
    } catch (err) {
      console.error('[VideoPlayer] 시간 업데이트 오류:', err);
    }
  }, [isDragging, onTimeUpdate, safeSetState]);

  const handlePlay = useCallback(() => {
    try {
      safeSetState(prev => ({ ...prev, isPlaying: true }));
      resetHideTimer();
      
      if (syncEnabled && onPlaybackSync) {
        onPlaybackSync({
          currentTime: state.currentTime,
          isPlaying: true,
          playbackRate: state.playbackRate
        });
      }
    } catch (err) {
      console.error('[VideoPlayer] 재생 이벤트 오류:', err);
    }
  }, [safeSetState, resetHideTimer, syncEnabled, onPlaybackSync, state.currentTime, state.playbackRate]);

  const handlePause = useCallback(() => {
    try {
      safeSetState(prev => ({ ...prev, isPlaying: false }));
      if (isMountedRef.current) {
        setShowControls(true);
      }
      
      if (syncEnabled && onPlaybackSync) {
        onPlaybackSync({
          currentTime: state.currentTime,
          isPlaying: false,
          playbackRate: state.playbackRate
        });
      }
    } catch (err) {
      console.error('[VideoPlayer] 일시정지 이벤트 오류:', err);
    }
  }, [safeSetState, syncEnabled, onPlaybackSync, state.currentTime, state.playbackRate]);

  const handleError = useCallback(() => {
    try {
      safeSetState(prev => ({ ...prev, isLoading: false }));
      setError('비디오를 재생할 수 없습니다. 파일을 확인해주세요.');
      console.error('[VideoPlayer] 비디오 오류 발생');
    } catch (err) {
      console.error('[VideoPlayer] 에러 핸들링 중 오류:', err);
    }
  }, [safeSetState]);

  // 재생/일시정지 토글 (안전성 강화)
  const togglePlayPause = useCallback(async () => {
    try {
      if (videoRef.current && isMountedRef.current) {
        if (state.isPlaying) {
          videoRef.current.pause();
        } else {
          const playPromise = videoRef.current.play();
          if (playPromise !== undefined) {
            await playPromise.catch(err => {
              console.error('[VideoPlayer] 재생 실패:', err);
              setError('비디오 재생에 실패했습니다.');
            });
          }
        }
      }
    } catch (err) {
      console.error('[VideoPlayer] 재생/일시정지 토글 오류:', err);
      setError('재생 제어 중 오류가 발생했습니다.');
    }
  }, [state.isPlaying]);

  // 음소거 토글
  const toggleMute = () => {
    if (videoRef.current) {
      const newMuted = !state.isMuted;
      videoRef.current.muted = newMuted;
      setState(prev => ({ ...prev, isMuted: newMuted }));
    }
  };

  // 볼륨 조절
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const volume = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.volume = volume;
      setState(prev => ({ ...prev, volume, isMuted: volume === 0 }));
    }
  };

  // 재생 속도 변경
  const handlePlaybackRateChange = (rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
      setState(prev => ({ ...prev, playbackRate: rate }));
      setShowSettings(false);
      
      if (syncEnabled && onPlaybackSync) {
        onPlaybackSync({
          currentTime: state.currentTime,
          isPlaying: state.isPlaying,
          playbackRate: rate
        });
      }
    }
  };

  // 진행바 클릭으로 시간 이동 (안전성 강화)
  const handleProgressClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    try {
      if (progressRef.current && videoRef.current && isMountedRef.current && state.duration > 0) {
        const rect = progressRef.current.getBoundingClientRect();
        if (rect.width > 0) {
          const clickX = e.clientX - rect.left;
          const percentage = Math.max(0, Math.min(1, clickX / rect.width));
          const newTime = percentage * state.duration;
          
          // 유효한 시간인지 확인
          if (isFinite(newTime) && newTime >= 0 && newTime <= state.duration) {
            videoRef.current.currentTime = newTime;
            safeSetState(prev => ({ ...prev, currentTime: newTime }));
          }
        }
      }
    } catch (err) {
      console.error('[VideoPlayer] 진행바 클릭 오류:', err);
    }
  }, [state.duration, safeSetState]);

  // 시간 포맷팅 (안전성 강화)
  const formatTime = useCallback((time: number): string => {
    try {
      if (!isFinite(time) || time < 0) return '0:00';
      const minutes = Math.floor(time / 60);
      const seconds = Math.floor(time % 60);
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    } catch {
      return '0:00';
    }
  }, []);

  // 전체화면 토글
  const toggleFullscreen = () => {
    if (containerRef.current) {
      if (!state.isFullscreen) {
        if (containerRef.current.requestFullscreen) {
          containerRef.current.requestFullscreen();
        }
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      }
    }
  };

  // 컴포넌트 언마운트 시 정리 작업
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (hideControlsTimeout.current) {
        clearTimeout(hideControlsTimeout.current);
      }
    };
  }, []);

  // 전체화면 상태 감지
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (isMountedRef.current) {
        setState(prev => ({
          ...prev,
          isFullscreen: !!document.fullscreenElement
        }));
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // 키보드 단축키
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target !== document.body) return;
      
      switch (e.key) {
        case ' ':
        case 'k':
          e.preventDefault();
          togglePlayPause();
          break;
        case 'm':
          toggleMute();
          break;
        case 'f':
          toggleFullscreen();
          break;
        case 'ArrowLeft':
          if (videoRef.current) {
            videoRef.current.currentTime = Math.max(0, state.currentTime - 10);
          }
          break;
        case 'ArrowRight':
          if (videoRef.current) {
            videoRef.current.currentTime = Math.min(state.duration, state.currentTime + 10);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [state.currentTime, state.duration, state.isPlaying]);

  // 비디오 클릭으로 피드백 추가
  const handleVideoClick = (e: React.MouseEvent<HTMLVideoElement>) => {
    if (!allowNewFeedbacks || e.detail !== 2) return; // 더블클릭만 처리
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    
    onAddFeedback?.(state.currentTime, { x, y });
  };

  // 피드백 마커 클릭
  const handleFeedbackMarkerClick = (feedback: TimelineFeedback, e: React.MouseEvent) => {
    e.stopPropagation();
    if (videoRef.current) {
      videoRef.current.currentTime = feedback.timestamp;
    }
    onFeedbackClick?.(feedback);
  };

  // 피드백 카테고리별 색상
  const getFeedbackColor = (category: string): string => {
    const colors: Record<string, string> = {
      general: '#6B7280',
      correction: '#DC2626',
      question: '#2563EB',
      approval: '#16A34A',
      suggestion: '#D97706',
      technical: '#9333EA',
      creative: '#EC4899'
    };
    return colors[category] || colors.general;
  };

  return (
    <div 
      ref={containerRef}
      className={`relative bg-black rounded-lg overflow-hidden group ${className}`}
      onMouseMove={resetHideTimer}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => state.isPlaying && setShowControls(false)}
    >
      {/* 비디오 요소 */}
      <video
        ref={videoRef}
        src={video.file_url}
        poster={video.thumbnail_url}
        className="w-full h-full object-contain cursor-pointer"
        onLoadedMetadata={handleLoadedMetadata}
        onTimeUpdate={handleTimeUpdate}
        onPlay={handlePlay}
        onPause={handlePause}
        onDoubleClick={handleVideoClick}
        onWaiting={() => safeSetState(prev => ({ ...prev, isLoading: true }))}
        onCanPlay={() => safeSetState(prev => ({ ...prev, isLoading: false }))}
        onError={handleError}
        onLoadStart={() => safeSetState(prev => ({ ...prev, isLoading: true }))}
        onLoadedData={() => safeSetState(prev => ({ ...prev, isLoading: false }))}
        preload="metadata"
      />

      {/* 에러 표시 */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
          <div className="text-center text-white p-6">
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">재생 오류</h3>
            <p className="text-sm text-gray-300 mb-4">{error}</p>
            <button
              onClick={() => {
                setError(null);
                if (videoRef.current) {
                  videoRef.current.load();
                }
              }}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors"
            >
              다시 시도
            </button>
          </div>
        </div>
      )}

      {/* 로딩 인디케이터 */}
      {state.isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      )}

      {/* 비디오 오버레이의 피드백 마커 */}
      {showFeedbackMarkers && feedbacks.map(feedback => (
        feedback.position && (
          <button
            key={feedback.id}
            className="absolute w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-white text-xs font-bold hover:scale-110 transition-transform z-10"
            style={{
              backgroundColor: getFeedbackColor(feedback.category),
              left: `${feedback.position.x * 100}%`,
              top: `${feedback.position.y * 100}%`,
              transform: 'translate(-50%, -50%)'
            }}
            onClick={(e) => handleFeedbackMarkerClick(feedback, e)}
            onMouseEnter={() => setHoveredFeedback(feedback.id)}
            onMouseLeave={() => setHoveredFeedback(null)}
            title={feedback.title}
          >
            <MessageSquare size={12} />
          </button>
        )
      ))}

      {/* 호버된 피드백 툴팁 */}
      {hoveredFeedback && (
        <div className="absolute z-20 bg-black bg-opacity-90 text-white p-2 rounded text-sm pointer-events-none">
          {feedbacks.find(f => f.id === hoveredFeedback)?.title}
        </div>
      )}

      {/* 컨트롤 오버레이 */}
      <div className={`absolute inset-x-0 bottom-0 bg-gradient-to-t from-black via-black/50 to-transparent p-4 transition-opacity duration-300 ${showControls ? 'opacity-100' : 'opacity-0'}`}>
        {/* 진행바 영역 */}
        <div className="mb-4">
          {/* 피드백 마커가 있는 진행바 */}
          <div 
            ref={progressRef}
            className="relative h-2 bg-white bg-opacity-20 rounded-full cursor-pointer hover:h-3 transition-all"
            onClick={handleProgressClick}
          >
            {/* 재생 진행 */}
            <div 
              className="absolute top-0 left-0 h-full bg-red-500 rounded-full"
              style={{ width: `${(state.currentTime / state.duration) * 100}%` }}
            />
            
            {/* 피드백 마커들 (타임라인) */}
            {showFeedbackMarkers && feedbacks.map(feedback => (
              <div
                key={feedback.id}
                className="absolute top-0 w-1 h-full rounded-full opacity-80 hover:opacity-100"
                style={{
                  backgroundColor: getFeedbackColor(feedback.category),
                  left: `${(feedback.timestamp / state.duration) * 100}%`,
                  transform: 'translateX(-50%)'
                }}
                title={`${formatTime(feedback.timestamp)} - ${feedback.title}`}
              />
            ))}
            
            {/* 재생 위치 핸들 */}
            <div 
              className="absolute top-1/2 w-4 h-4 bg-red-500 rounded-full transform -translate-y-1/2 shadow-lg"
              style={{ left: `${(state.currentTime / state.duration) * 100}%`, transform: 'translate(-50%, -50%)' }}
            />
          </div>
        </div>

        {/* 컨트롤 버튼들 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* 재생/일시정지 */}
            <button
              onClick={togglePlayPause}
              className="text-white hover:text-red-500 transition-colors"
            >
              {state.isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>

            {/* 뒤로/앞으로 10초 */}
            <button
              onClick={() => videoRef.current && (videoRef.current.currentTime = Math.max(0, state.currentTime - 10))}
              className="text-white hover:text-red-500 transition-colors"
            >
              <RotateCcw size={20} />
            </button>
            <button
              onClick={() => videoRef.current && (videoRef.current.currentTime = Math.min(state.duration, state.currentTime + 10))}
              className="text-white hover:text-red-500 transition-colors"
            >
              <RotateCw size={20} />
            </button>

            {/* 볼륨 */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className="text-white hover:text-red-500 transition-colors"
              >
                {state.isMuted || state.volume === 0 ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={state.isMuted ? 0 : state.volume}
                onChange={handleVolumeChange}
                className="w-20 accent-red-500"
              />
            </div>

            {/* 시간 표시 */}
            <div className="text-white text-sm">
              {formatTime(state.currentTime)} / {formatTime(state.duration)}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* 피드백 추가 버튼 */}
            {allowNewFeedbacks && (
              <button
                onClick={() => onAddFeedback?.(state.currentTime)}
                className="text-white hover:text-red-500 transition-colors"
                title="현재 시점에 피드백 추가"
              >
                <Plus size={20} />
              </button>
            )}

            {/* 설정 메뉴 */}
            <div className="relative">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="text-white hover:text-red-500 transition-colors"
              >
                <Settings size={20} />
              </button>
              
              {showSettings && (
                <div className="absolute bottom-full right-0 mb-2 bg-black bg-opacity-90 rounded-lg p-3 min-w-40">
                  <div className="text-white text-sm font-medium mb-2">재생 속도</div>
                  <div className="space-y-1">
                    {[0.5, 0.75, 1, 1.25, 1.5, 2].map(rate => (
                      <button
                        key={rate}
                        onClick={() => handlePlaybackRateChange(rate)}
                        className={`block w-full text-left px-2 py-1 text-sm rounded hover:bg-white hover:bg-opacity-20 ${state.playbackRate === rate ? 'text-red-500' : 'text-white'}`}
                      >
                        {rate}x
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 전체화면 */}
            <button
              onClick={toggleFullscreen}
              className="text-white hover:text-red-500 transition-colors"
            >
              <Maximize size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* 재생 버튼 오버레이 (중앙) */}
      {!state.isPlaying && !state.isLoading && (
        <button
          onClick={togglePlayPause}
          className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 hover:bg-opacity-40 transition-colors"
        >
          <Play size={64} className="text-white" />
        </button>
      )}
    </div>
  );
}