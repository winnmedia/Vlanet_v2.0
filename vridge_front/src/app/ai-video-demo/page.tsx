'use client';

import React, { useState } from 'react';
import { 
  StoryEditor, 
  SceneTimeline, 
  PromptBuilder, 
  GenerationProgress, 
  VideoPreview 
} from '@/components/ai-video';
import { useAIVideoStore } from '@/store/ai-video.store';
import { Story, Scene } from '@/types/ai-video';

export default function AIVideoDemoPage() {
  const {
    currentStory,
    scenes,
    generationProgress,
    promptTemplates,
    setCurrentStory,
    generateVideo
  } = useAIVideoStore();

  const [selectedScene, setSelectedScene] = useState<Scene | null>(null);
  const [showStoryEditor, setShowStoryEditor] = useState(!currentStory);

  const handleStorySave = (storyData: Partial<Story>) => {
    const story: Story = {
      id: storyData.id || crypto.randomUUID(),
      title: storyData.title || '',
      description: storyData.description || '',
      totalDuration: 0,
      scenes: [],
      createdAt: storyData.createdAt || new Date(),
      updatedAt: new Date(),
      status: 'draft',
      ...storyData
    };
    
    setCurrentStory(story);
    setShowStoryEditor(false);
  };

  const handleSceneSelect = (scene: Scene) => {
    setSelectedScene(scene);
  };

  const handleSceneReorder = (fromIndex: number, toIndex: number) => {
    // This is handled by the store through useAIVideoStore().reorderScenes
  };

  const handleSceneUpdate = (id: string, updates: Partial<Scene>) => {
    // This is handled by the store through useAIVideoStore().updateScene
  };

  const handlePromptGenerate = async (prompt: string) => {
    if (!selectedScene) {
      alert('  .');
      return;
    }

    try {
      await generateVideo({
        sceneId: selectedScene.id,
        prompt,
        duration: selectedScene.duration,
        quality: 'medium'
      });
    } catch (error) {
      console.error('Video generation failed:', error);
    }
  };

  const handleGenerationCancel = (sceneId: string) => {
    // In a real implementation, this would cancel the generation request
    console.log('Canceling generation for scene:', sceneId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI   
              </h1>
              <p className="text-gray-600 mt-2">
                AI    
              </p>
            </div>
            
            {currentStory && (
              <button
                onClick={() => setShowStoryEditor(true)}
                className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200 transition-colors"
              >
                 
              </button>
            )}
          </div>

          {currentStory && (
            <div className="mt-4 p-4 bg-white rounded-lg border">
              <h2 className="font-semibold text-lg text-gray-900">
                {currentStory.title}
              </h2>
              <p className="text-gray-600 mt-1">
                {currentStory.description}
              </p>
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                <span>{scenes.length} </span>
                <span> {Math.round(currentStory.totalDuration / 60 * 10) / 10}</span>
                <span>: {currentStory.status}</span>
              </div>
            </div>
          )}
        </div>

        {/* Story Editor Modal */}
        {showStoryEditor && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <StoryEditor
                story={currentStory || undefined}
                onSave={handleStorySave}
                onCancel={() => setShowStoryEditor(false)}
              />
            </div>
          </div>
        )}

        {/* Main Content */}
        {currentStory ? (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Left Column - Timeline and Controls */}
            <div className="xl:col-span-2 space-y-8">
              {/* Scene Timeline */}
              <SceneTimeline
                scenes={scenes}
                onSceneSelect={handleSceneSelect}
                onSceneReorder={handleSceneReorder}
                onSceneUpdate={handleSceneUpdate}
              />

              {/* Prompt Builder */}
              {selectedScene && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium text-blue-800">
                       : {selectedScene.title}
                    </span>
                  </div>
                </div>
              )}

              <PromptBuilder
                initialPrompt={selectedScene?.prompt || ''}
                templates={promptTemplates}
                onPromptChange={(prompt) => {
                  if (selectedScene) {
                    handleSceneUpdate(selectedScene.id, { prompt });
                  }
                }}
                onGenerate={handlePromptGenerate}
              />
            </div>

            {/* Right Column - Video Preview */}
            <div className="space-y-8">
              <VideoPreview
                scenes={scenes}
                currentScene={selectedScene || undefined}
                onSceneChange={setSelectedScene}
                autoPlay={false}
              />

              {/* Quick Stats */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="font-medium text-gray-900 mb-3"> </h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600"> </span>
                    <span className="font-medium">{scenes.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600"> </span>
                    <span className="font-medium text-green-600">
                      {scenes.filter(s => s.status === 'completed').length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">  </span>
                    <span className="font-medium text-blue-600">
                      {scenes.filter(s => s.status === 'generating').length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600"> </span>
                    <span className="font-medium text-red-600">
                      {scenes.filter(s => s.status === 'error').length}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="text-gray-400 mb-6">
              <svg className="w-24 h-24 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                 
            </h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
                AI    
            </p>
            <button
              onClick={() => setShowStoryEditor(true)}
              className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
               
            </button>
          </div>
        )}

        {/* Generation Progress */}
        <GenerationProgress
          progress={generationProgress}
          onCancel={handleGenerationCancel}
        />
      </div>
    </div>
  );
}