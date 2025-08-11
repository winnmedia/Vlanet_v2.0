'use client';

import React, { useEffect, useState } from 'react';
import { GenerationProgressProps, GenerationProgress as ProgressType } from '@/types/ai-video';
import { useAIVideoStore } from '@/store/ai-video.store';

interface ProgressItemProps {
  progress: ProgressType;
  sceneName: string;
  onCancel?: () => void;
}

const ProgressItem: React.FC<ProgressItemProps> = ({ progress, sceneName, onCancel }) => {
  const [timeElapsed, setTimeElapsed] = useState(0);

  useEffect(() => {
    if (progress.status !== 'processing' || !progress.startedAt) return;

    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - progress.startedAt!.getTime()) / 1000);
      setTimeElapsed(elapsed);
    }, 1000);

    return () => clearInterval(interval);
  }, [progress.status, progress.startedAt]);

  const getStatusColor = (status: ProgressType['status']) => {
    switch (status) {
      case 'queued': return 'text-yellow-600 bg-yellow-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'completed': return 'text-green-600 bg-green-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: ProgressType['status']) => {
    switch (status) {
      case 'queued':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        );
      case 'processing':
        return (
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        );
      case 'completed':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getEstimatedRemaining = () => {
    if (!progress.estimatedTime || progress.status !== 'processing') return null;
    const remaining = Math.max(0, progress.estimatedTime - timeElapsed);
    return remaining;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-center space-x-3 mb-3">
            <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(progress.status)}`}>
              {getStatusIcon(progress.status)}
              <span className="ml-1 capitalize">
                {progress.status === 'queued' ? '' :
                 progress.status === 'processing' ? '' :
                 progress.status === 'completed' ? '' :
                 progress.status === 'error' ? '' : progress.status}
              </span>
            </div>
            <h3 className="font-medium text-gray-900">{sceneName}</h3>
          </div>

          {/* Progress Bar */}
          {progress.status === 'processing' && (
            <div className="mb-3">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                <span>{progress.progress}% </span>
                <span>{formatTime(timeElapsed)} </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress.progress}%` }}
                />
              </div>
              {getEstimatedRemaining() && (
                <div className="text-xs text-gray-500 mt-1">
                   {formatTime(getEstimatedRemaining()!)} 
                </div>
              )}
            </div>
          )}

          {/* Completion Info */}
          {progress.status === 'completed' && progress.completedAt && (
            <div className="text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <span>  </span>
                <span>
                  {progress.completedAt.toLocaleTimeString('ko-KR', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
            </div>
          )}

          {/* Error Info */}
          {progress.status === 'error' && progress.errorMessage && (
            <div className="text-sm text-red-600 bg-red-50 rounded p-2">
              <div className="font-medium"> :</div>
              <div>{progress.errorMessage}</div>
            </div>
          )}

          {/* Queue Info */}
          {progress.status === 'queued' && (
            <div className="text-sm text-gray-600">
                
            </div>
          )}
        </div>

        {/* Cancel Button */}
        {(progress.status === 'queued' || progress.status === 'processing') && onCancel && (
          <button
            onClick={onCancel}
            className="ml-4 p-2 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
            title=""
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export const GenerationProgress: React.FC<GenerationProgressProps> = ({ 
  progress, 
  onCancel 
}) => {
  const { scenes } = useAIVideoStore();
  const [isMinimized, setIsMinimized] = useState(false);

  const progressEntries = Object.entries(progress);
  const hasActiveProgress = progressEntries.some(([_, prog]) => 
    prog.status === 'processing' || prog.status === 'queued'
  );

  const getSceneName = (sceneId: string) => {
    const scene = scenes.find(s => s.id === sceneId);
    return scene?.title || ` ${sceneId.slice(0, 8)}`;
  };

  const completedCount = progressEntries.filter(([_, prog]) => prog.status === 'completed').length;
  const totalCount = progressEntries.length;
  const errorCount = progressEntries.filter(([_, prog]) => prog.status === 'error').length;

  if (progressEntries.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 max-w-md w-full z-50">
      <div className="bg-white rounded-lg shadow-xl border border-gray-200">
        {/* Header */}
        <div 
          className="flex items-center justify-between p-4 border-b cursor-pointer"
          onClick={() => setIsMinimized(!isMinimized)}
        >
          <div className="flex items-center space-x-3">
            <h3 className="font-semibold text-gray-900">  </h3>
            {hasActiveProgress && (
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Progress Summary */}
            <div className="text-sm text-gray-600">
              {completedCount}/{totalCount}
              {errorCount > 0 && (
                <span className="text-red-500 ml-1">({errorCount} )</span>
              )}
            </div>
            
            {/* Minimize Button */}
            <button 
              className="p-1 hover:bg-gray-100 rounded"
              title={isMinimized ? '' : ''}
            >
              <svg 
                className={`w-4 h-4 text-gray-400 transition-transform ${isMinimized ? 'rotate-180' : ''}`}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        {!isMinimized && (
          <div className="max-h-96 overflow-y-auto">
            <div className="p-4 space-y-3">
              {progressEntries.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                     
                </div>
              ) : (
                progressEntries
                  .sort(([, a], [, b]) => {
                    // Sort by status priority: processing > queued > error > completed
                    const statusPriority = {
                      processing: 4,
                      queued: 3,
                      error: 2,
                      completed: 1
                    };
                    return (statusPriority[b.status] || 0) - (statusPriority[a.status] || 0);
                  })
                  .map(([sceneId, prog]) => (
                    <ProgressItem
                      key={sceneId}
                      progress={prog}
                      sceneName={getSceneName(sceneId)}
                      onCancel={onCancel ? () => onCancel(sceneId) : undefined}
                    />
                  ))
              )}
            </div>

            {/* Overall Progress */}
            {totalCount > 0 && (
              <div className="px-4 pb-4 border-t bg-gray-50">
                <div className="pt-3">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                    <span> </span>
                    <span>{Math.round((completedCount / totalCount) * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className="bg-green-600 h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${(completedCount / totalCount) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Minimized Summary */}
        {isMinimized && hasActiveProgress && (
          <div className="px-4 pb-3">
            <div className="text-sm text-gray-600">
              {progressEntries.filter(([_, prog]) => prog.status === 'processing').length > 0 && (
                <span>   ...</span>
              )}
              {progressEntries.filter(([_, prog]) => prog.status === 'queued').length > 0 && (
                <span>⏳   </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};