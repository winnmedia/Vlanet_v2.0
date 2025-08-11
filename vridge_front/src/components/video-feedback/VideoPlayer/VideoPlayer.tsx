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

  //    
  const hideControlsTimeout = useRef<NodeJS.Timeout>();

  //    
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

  //    ( )
  const handleLoadedMetadata = useCallback(() => {
    try {
      if (videoRef.current && isMountedRef.current) {
        const duration = videoRef.current.duration;
        // NaN    
        if (isFinite(duration) && duration > 0) {
          safeSetState(prev => ({
            ...prev,
            duration,
            isLoading: false
          }));
          setError(null);
        } else {
          setError('    .');
        }
      }
    } catch (err) {
      console.error('[VideoPlayer]   :', err);
      setError('     .');
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
      console.error('[VideoPlayer]   :', err);
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
      console.error('[VideoPlayer]   :', err);
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
      console.error('[VideoPlayer]   :', err);
    }
  }, [safeSetState, syncEnabled, onPlaybackSync, state.currentTime, state.playbackRate]);

  const handleError = useCallback(() => {
    try {
      safeSetState(prev => ({ ...prev, isLoading: false }));
      setError('   .  .');
      console.error('[VideoPlayer]   ');
    } catch (err) {
      console.error('[VideoPlayer]    :', err);
    }
  }, [safeSetState]);

  // /  ( )
  const togglePlayPause = useCallback(async () => {
    try {
      if (videoRef.current && isMountedRef.current) {
        if (state.isPlaying) {
          videoRef.current.pause();
        } else {
          const playPromise = videoRef.current.play();
          if (playPromise !== undefined) {
            await playPromise.catch(err => {
              console.error('[VideoPlayer]  :', err);
              setError('  .');
            });
          }
        }
      }
    } catch (err) {
      console.error('[VideoPlayer] /  :', err);
      setError('    .');
    }
  }, [state.isPlaying]);

  //  
  const toggleMute = () => {
    if (videoRef.current) {
      const newMuted = !state.isMuted;
      videoRef.current.muted = newMuted;
      setState(prev => ({ ...prev, isMuted: newMuted }));
    }
  };

  //  
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const volume = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.volume = volume;
      setState(prev => ({ ...prev, volume, isMuted: volume === 0 }));
    }
  };

  //   
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

  //     ( )
  const handleProgressClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    try {
      if (progressRef.current && videoRef.current && isMountedRef.current && state.duration > 0) {
        const rect = progressRef.current.getBoundingClientRect();
        if (rect.width > 0) {
          const clickX = e.clientX - rect.left;
          const percentage = Math.max(0, Math.min(1, clickX / rect.width));
          const newTime = percentage * state.duration;
          
          //   
          if (isFinite(newTime) && newTime >= 0 && newTime <= state.duration) {
            videoRef.current.currentTime = newTime;
            safeSetState(prev => ({ ...prev, currentTime: newTime }));
          }
        }
      }
    } catch (err) {
      console.error('[VideoPlayer]   :', err);
    }
  }, [state.duration, safeSetState]);

  //   ( )
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

  //  
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

  //     
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (hideControlsTimeout.current) {
        clearTimeout(hideControlsTimeout.current);
      }
    };
  }, []);

  //   
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

  //  
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

  //    
  const handleVideoClick = (e: React.MouseEvent<HTMLVideoElement>) => {
    if (!allowNewFeedbacks || e.detail !== 2) return; //  
    
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    
    onAddFeedback?.(state.currentTime, { x, y });
  };

  //   
  const handleFeedbackMarkerClick = (feedback: TimelineFeedback, e: React.MouseEvent) => {
    e.stopPropagation();
    if (videoRef.current) {
      videoRef.current.currentTime = feedback.timestamp;
    }
    onFeedbackClick?.(feedback);
  };

  //   
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
      {/*   */}
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

      {/*   */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
          <div className="text-center text-white p-6">
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2"> </h3>
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
               
            </button>
          </div>
        </div>
      )}

      {/*   */}
      {state.isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      )}

      {/*     */}
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

      {/*    */}
      {hoveredFeedback && (
        <div className="absolute z-20 bg-black bg-opacity-90 text-white p-2 rounded text-sm pointer-events-none">
          {feedbacks.find(f => f.id === hoveredFeedback)?.title}
        </div>
      )}

      {/*   */}
      <div className={`absolute inset-x-0 bottom-0 bg-gradient-to-t from-black via-black/50 to-transparent p-4 transition-opacity duration-300 ${showControls ? 'opacity-100' : 'opacity-0'}`}>
        {/*   */}
        <div className="mb-4">
          {/*     */}
          <div 
            ref={progressRef}
            className="relative h-2 bg-white bg-opacity-20 rounded-full cursor-pointer hover:h-3 transition-all"
            onClick={handleProgressClick}
          >
            {/*   */}
            <div 
              className="absolute top-0 left-0 h-full bg-red-500 rounded-full"
              style={{ width: `${(state.currentTime / state.duration) * 100}%` }}
            />
            
            {/*   () */}
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
            
            {/*    */}
            <div 
              className="absolute top-1/2 w-4 h-4 bg-red-500 rounded-full transform -translate-y-1/2 shadow-lg"
              style={{ left: `${(state.currentTime / state.duration) * 100}%`, transform: 'translate(-50%, -50%)' }}
            />
          </div>
        </div>

        {/*   */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* / */}
            <button
              onClick={togglePlayPause}
              className="text-white hover:text-red-500 transition-colors"
            >
              {state.isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>

            {/* / 10 */}
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

            {/*  */}
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

            {/*   */}
            <div className="text-white text-sm">
              {formatTime(state.currentTime)} / {formatTime(state.duration)}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/*    */}
            {allowNewFeedbacks && (
              <button
                onClick={() => onAddFeedback?.(state.currentTime)}
                className="text-white hover:text-red-500 transition-colors"
                title="   "
              >
                <Plus size={20} />
              </button>
            )}

            {/*   */}
            <div className="relative">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="text-white hover:text-red-500 transition-colors"
              >
                <Settings size={20} />
              </button>
              
              {showSettings && (
                <div className="absolute bottom-full right-0 mb-2 bg-black bg-opacity-90 rounded-lg p-3 min-w-40">
                  <div className="text-white text-sm font-medium mb-2"> </div>
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

            {/*  */}
            <button
              onClick={toggleFullscreen}
              className="text-white hover:text-red-500 transition-colors"
            >
              <Maximize size={20} />
            </button>
          </div>
        </div>
      </div>

      {/*    () */}
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