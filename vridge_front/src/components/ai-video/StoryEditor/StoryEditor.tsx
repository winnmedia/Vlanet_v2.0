'use client';

import React, { useState, useEffect } from 'react';
import { StoryEditorProps, Story } from '@/types/ai-video';
import { useAIVideoStore } from '@/store/ai-video.store';

export const StoryEditor: React.FC<StoryEditorProps> = ({
  story,
  onSave,
  onCancel
}) => {
  const [title, setTitle] = useState(story?.title || '');
  const [description, setDescription] = useState(story?.description || '');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isDirty, setIsDirty] = useState(false);

  const { currentStory, setCurrentStory } = useAIVideoStore();

  useEffect(() => {
    if (story) {
      setTitle(story.title);
      setDescription(story.description);
    }
  }, [story]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = '스토리 제목을 입력해주세요.';
    } else if (title.length > 100) {
      newErrors.title = '제목은 100자 이하로 입력해주세요.';
    }

    if (!description.trim()) {
      newErrors.description = '스토리 설명을 입력해주세요.';
    } else if (description.length > 500) {
      newErrors.description = '설명은 500자 이하로 입력해주세요.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validateForm()) return;

    const storyData: Partial<Story> = {
      title: title.trim(),
      description: description.trim(),
      updatedAt: new Date(),
      ...(story && { id: story.id }),
      ...(!story && { 
        id: crypto.randomUUID(),
        createdAt: new Date(),
        scenes: [],
        totalDuration: 0,
        status: 'draft' as const
      })
    };

    onSave(storyData);
    setIsDirty(false);
  };

  const handleReset = () => {
    if (story) {
      setTitle(story.title);
      setDescription(story.description);
    } else {
      setTitle('');
      setDescription('');
    }
    setErrors({});
    setIsDirty(false);
  };

  const handleTitleChange = (value: string) => {
    setTitle(value);
    setIsDirty(true);
    if (errors.title && value.trim()) {
      setErrors(prev => ({ ...prev, title: '' }));
    }
  };

  const handleDescriptionChange = (value: string) => {
    setDescription(value);
    setIsDirty(true);
    if (errors.description && value.trim()) {
      setErrors(prev => ({ ...prev, description: '' }));
    }
  };

  const handleCancel = () => {
    if (isDirty) {
      if (window.confirm('변경사항이 저장되지 않습니다. 정말 취소하시겠습니까?')) {
        handleReset();
        onCancel?.();
      }
    } else {
      onCancel?.();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {story ? '스토리 편집' : '새 스토리 생성'}
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isDirty ? 'bg-orange-500' : 'bg-green-500'}`} />
          <span className="text-sm text-gray-500">
            {isDirty ? '수정됨' : '저장됨'}
          </span>
        </div>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); handleSave(); }} className="space-y-6">
        {/* Title Input */}
        <div>
          <label htmlFor="story-title" className="block text-sm font-medium text-gray-700 mb-2">
            스토리 제목 <span className="text-red-500">*</span>
          </label>
          <input
            id="story-title"
            type="text"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="흥미로운 스토리 제목을 입력하세요"
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              errors.title ? 'border-red-500' : 'border-gray-300'
            }`}
            maxLength={100}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            {title.length}/100 자
          </p>
        </div>

        {/* Description Textarea */}
        <div>
          <label htmlFor="story-description" className="block text-sm font-medium text-gray-700 mb-2">
            스토리 설명 <span className="text-red-500">*</span>
          </label>
          <textarea
            id="story-description"
            value={description}
            onChange={(e) => handleDescriptionChange(e.target.value)}
            placeholder="스토리의 전체적인 내용과 컨셉을 설명해주세요"
            rows={6}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors resize-vertical ${
              errors.description ? 'border-red-500' : 'border-gray-300'
            }`}
            maxLength={500}
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description}</p>
          )}
          <p className="mt-1 text-sm text-gray-500">
            {description.length}/500 자
          </p>
        </div>

        {/* Story Info */}
        {story && (
          <div className="bg-gray-50 rounded-lg p-4 space-y-2">
            <h3 className="font-medium text-gray-900 mb-3">스토리 정보</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">생성일:</span>
                <span className="ml-2 text-gray-900">
                  {story.createdAt?.toLocaleDateString('ko-KR')}
                </span>
              </div>
              <div>
                <span className="text-gray-600">수정일:</span>
                <span className="ml-2 text-gray-900">
                  {story.updatedAt?.toLocaleDateString('ko-KR')}
                </span>
              </div>
              <div>
                <span className="text-gray-600">씬 개수:</span>
                <span className="ml-2 text-gray-900">
                  {story.scenes?.length || 0}개
                </span>
              </div>
              <div>
                <span className="text-gray-600">총 길이:</span>
                <span className="ml-2 text-gray-900">
                  {Math.round((story.totalDuration || 0) / 60 * 10) / 10}분
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-3 pt-6 border-t">
          <button
            type="button"
            onClick={handleReset}
            disabled={!isDirty}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            초기화
          </button>
          
          {onCancel && (
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
          )}
          
          <button
            type="submit"
            disabled={!isDirty && !(!story && title && description)}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {story ? '수정하기' : '생성하기'}
          </button>
        </div>
      </form>
    </div>
  );
};