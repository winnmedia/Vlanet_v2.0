'use client';

import React, { useState, useRef, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { SceneTimelineProps, Scene } from '@/types/ai-video';
import { useAIVideoStore } from '@/store/ai-video.store';

interface SceneCardProps {
  scene: Scene;
  index: number;
  isSelected: boolean;
  onClick: () => void;
  onUpdate: (updates: Partial<Scene>) => void;
  onDelete: () => void;
}

const SceneCard: React.FC<SceneCardProps> = ({ 
  scene, 
  index, 
  isSelected, 
  onClick, 
  onUpdate,
  onDelete 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(scene.title);
  const [editedDescription, setEditedDescription] = useState(scene.description);

  const getStatusColor = (status: Scene['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-100 border-green-300 text-green-800';
      case 'generating': return 'bg-blue-100 border-blue-300 text-blue-800';
      case 'error': return 'bg-red-100 border-red-300 text-red-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getStatusIcon = (status: Scene['status']) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'generating':
        return (
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
        );
    }
  };

  const handleSaveEdit = () => {
    onUpdate({
      title: editedTitle.trim(),
      description: editedDescription.trim()
    });
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedTitle(scene.title);
    setEditedDescription(scene.description);
    setIsEditing(false);
  };

  return (
    <div
      className={`relative bg-white rounded-lg border-2 p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
        isSelected ? 'border-blue-500 shadow-lg ring-2 ring-blue-200' : 'border-gray-200'
      }`}
      onClick={onClick}
    >
      {/* Scene Number */}
      <div className="absolute -top-3 -left-3 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
        {index + 1}
      </div>

      {/* Status Badge */}
      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mb-3 ${getStatusColor(scene.status)}`}>
        {getStatusIcon(scene.status)}
        <span className="ml-1 capitalize">{scene.status}</span>
      </div>

      {/* Content */}
      {isEditing ? (
        <div className="space-y-3">
          <input
            type="text"
            value={editedTitle}
            onChange={(e) => setEditedTitle(e.target.value)}
            className="w-full px-2 py-1 text-sm font-medium border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="씬 제목"
            autoFocus
          />
          <textarea
            value={editedDescription}
            onChange={(e) => setEditedDescription(e.target.value)}
            className="w-full px-2 py-1 text-sm text-gray-600 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={2}
            placeholder="씬 설명"
          />
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleSaveEdit();
              }}
              className="px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
            >
              저장
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleCancelEdit();
              }}
              className="px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
            >
              취소
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900 line-clamp-2">
            {scene.title || `씬 ${index + 1}`}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-3">
            {scene.description || '설명이 없습니다.'}
          </p>
          
          {/* Duration */}
          <div className="flex items-center justify-between text-xs text-gray-500 mt-3">
            <span>{scene.duration}초</span>
            {scene.generatedAt && (
              <span>
                {scene.generatedAt.toLocaleDateString('ko-KR', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            )}
          </div>

          {/* Thumbnail */}
          {scene.thumbnailUrl && (
            <div className="mt-3">
              <img
                src={scene.thumbnailUrl}
                alt={`씬 ${index + 1} 썸네일`}
                className="w-full h-20 object-cover rounded"
              />
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="flex items-center space-x-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
            title="편집"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm('이 씬을 삭제하시겠습니까?')) {
                onDelete();
              }
            }}
            className="p-1 text-gray-400 hover:text-red-500 rounded"
            title="삭제"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export const SceneTimeline: React.FC<SceneTimelineProps> = ({
  scenes,
  onSceneSelect,
  onSceneReorder,
  onSceneUpdate
}) => {
  const [selectedSceneId, setSelectedSceneId] = useState<string | null>(null);
  const { addScene, removeScene } = useAIVideoStore();

  const handleDragEnd = useCallback((result: DropResult) => {
    if (!result.destination) return;

    const fromIndex = result.source.index;
    const toIndex = result.destination.index;

    if (fromIndex !== toIndex) {
      onSceneReorder(fromIndex, toIndex);
    }
  }, [onSceneReorder]);

  const handleSceneSelect = useCallback((scene: Scene) => {
    setSelectedSceneId(scene.id);
    onSceneSelect(scene);
  }, [onSceneSelect]);

  const handleAddScene = () => {
    const newScene = {
      title: `새 씬 ${scenes.length + 1}`,
      description: '씬 설명을 입력하세요',
      prompt: '',
      duration: 5,
      position: scenes.length,
      status: 'draft' as const
    };
    addScene(newScene);
  };

  const totalDuration = scenes.reduce((sum, scene) => sum + scene.duration, 0);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">씬 타임라인</h2>
          <p className="text-sm text-gray-600 mt-1">
            총 {scenes.length}개 씬 · {Math.round(totalDuration / 60 * 10) / 10}분
          </p>
        </div>
        
        <button
          onClick={handleAddScene}
          className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          씬 추가
        </button>
      </div>

      {/* Timeline Progress */}
      {scenes.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
            <span>0초</span>
            <span>{totalDuration}초</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            {scenes.map((scene, index) => {
              const startTime = scenes.slice(0, index).reduce((sum, s) => sum + s.duration, 0);
              const width = (scene.duration / totalDuration) * 100;
              const left = (startTime / totalDuration) * 100;
              
              return (
                <div
                  key={scene.id}
                  className={`absolute h-2 rounded-full transition-all duration-300 ${
                    scene.status === 'completed' ? 'bg-green-500' :
                    scene.status === 'generating' ? 'bg-blue-500' :
                    scene.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                  }`}
                  style={{
                    left: `${left}%`,
                    width: `${width}%`
                  }}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Scene Cards */}
      {scenes.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            아직 씬이 없습니다
          </h3>
          <p className="text-gray-600 mb-6">
            첫 번째 씬을 추가해서 스토리를 시작해보세요
          </p>
          <button
            onClick={handleAddScene}
            className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            첫 씬 추가하기
          </button>
        </div>
      ) : (
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="scenes" direction="horizontal">
            {(provided, snapshot) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className={`flex space-x-4 pb-4 overflow-x-auto ${
                  snapshot.isDraggingOver ? 'bg-blue-50 rounded-lg p-2' : ''
                }`}
              >
                {scenes.map((scene, index) => (
                  <Draggable key={scene.id} draggableId={scene.id} index={index}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={`group min-w-[280px] ${
                          snapshot.isDragging ? 'rotate-3 scale-105 shadow-2xl' : ''
                        }`}
                      >
                        <SceneCard
                          scene={scene}
                          index={index}
                          isSelected={selectedSceneId === scene.id}
                          onClick={() => handleSceneSelect(scene)}
                          onUpdate={(updates) => onSceneUpdate(scene.id, updates)}
                          onDelete={() => removeScene(scene.id)}
                        />
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      )}
    </div>
  );
};