'use client';

import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Image, Download, RefreshCw, Eye, Clock, CheckCircle, AlertCircle, Zap } from 'lucide-react';

interface Scene {
  id: string;
  order: number;
  title: string;
  description: string;
  duration: number;
  scene_type: string;
  preview_image_url?: string;
}

interface StoryboardGeneratorProps {
  storyId: string;
  scenes: Scene[];
  onStoryboardGenerated?: (storyboardData: any) => void;
  onSceneUpdated?: (sceneId: string, imageUrl: string) => void;
}

export const StoryboardGenerator: React.FC<StoryboardGeneratorProps> = ({
  storyId,
  scenes,
  onStoryboardGenerated,
  onSceneUpdated
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatingScenes, setGeneratingScenes] = useState<Set<string>>(new Set());
  const [progress, setProgress] = useState(0);
  const [generatedImages, setGeneratedImages] = useState<Record<string, string>>({});
  const [error, setError] = useState<string>('');
  const [completedScenes, setCompletedScenes] = useState<Set<string>>(new Set());

  // 전체 스토리보드 생성
  const generateAllStoryboards = useCallback(async () => {
    if (!storyId || scenes.length === 0) return;

    setIsGenerating(true);
    setError('');
    setProgress(0);

    try {
      const response = await fetch(`/api/ai-video/stories/${storyId}/generate-storyboard/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      
      if (response.ok && data.storyboard_urls) {
        const newImages: Record<string, string> = {};
        const newCompleted = new Set<string>();

        data.storyboard_urls.forEach((item: any) => {
          if (item.preview_url) {
            newImages[item.scene_id] = item.preview_url;
            newCompleted.add(item.scene_id);
          }
        });

        setGeneratedImages(prev => ({ ...prev, ...newImages }));
        setCompletedScenes(prev => new Set([...prev, ...newCompleted]));
        setProgress(100);

        onStoryboardGenerated?.(data);
      } else {
        setError(data.error || '스토리보드 생성 중 오류가 발생했습니다.');
      }
    } catch (err) {
      setError('네트워크 오류가 발생했습니다.');
      console.error('스토리보드 생성 오류:', err);
    } finally {
      setIsGenerating(false);
    }
  }, [storyId, scenes, onStoryboardGenerated]);

  // 개별 씬 스토리보드 생성
  const generateSceneStoryboard = useCallback(async (sceneId: string) => {
    if (generatingScenes.has(sceneId)) return;

    setGeneratingScenes(prev => new Set(prev).add(sceneId));
    setError('');

    try {
      const response = await fetch(`/api/ai-video/scenes/${sceneId}/generate-storyboard-image/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      
      if (response.ok && data.preview_url) {
        setGeneratedImages(prev => ({
          ...prev,
          [sceneId]: data.preview_url
        }));
        setCompletedScenes(prev => new Set(prev).add(sceneId));
        onSceneUpdated?.(sceneId, data.preview_url);
      } else {
        setError(data.error || `씬 ${sceneId} 스토리보드 생성 실패`);
      }
    } catch (err) {
      setError('네트워크 오류가 발생했습니다.');
      console.error('씬 스토리보드 생성 오류:', err);
    } finally {
      setGeneratingScenes(prev => {
        const next = new Set(prev);
        next.delete(sceneId);
        return next;
      });
    }
  }, [generatingScenes, onSceneUpdated]);

  // 모든 이미지 다운로드 (ZIP)
  const downloadAllImages = useCallback(async () => {
    const imageUrls = Object.values(generatedImages).filter(Boolean);
    
    if (imageUrls.length === 0) {
      setError('다운로드할 이미지가 없습니다.');
      return;
    }

    try {
      // 실제 구현에서는 ZIP 생성 API를 호출하거나
      // 클라이언트에서 직접 ZIP을 생성할 수 있습니다
      alert(`${imageUrls.length}개의 스토리보드 이미지를 다운로드합니다.`);
    } catch (err) {
      setError('다운로드 중 오류가 발생했습니다.');
      console.error('다운로드 오류:', err);
    }
  }, [generatedImages]);

  const getSceneTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      intro: '인트로',
      main: '메인',
      transition: '전환',
      outro: '아웃트로',
      text_overlay: '텍스트',
      b_roll: 'B롤'
    };
    return types[type] || type;
  };

  const getSceneTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      intro: 'bg-green-100 text-green-800',
      main: 'bg-blue-100 text-blue-800',
      transition: 'bg-yellow-100 text-yellow-800',
      outro: 'bg-red-100 text-red-800',
      text_overlay: 'bg-purple-100 text-purple-800',
      b_roll: 'bg-gray-100 text-gray-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const completionPercentage = scenes.length > 0 ? (completedScenes.size / scenes.length) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* 헤더 및 전체 제어 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">스토리보드 생성</h2>
          <p className="text-gray-600 mt-1">
            AI 기반 씬별 비주얼 콘티 자동 생성
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            onClick={generateAllStoryboards}
            disabled={isGenerating || scenes.length === 0}
            size="lg"
            className="px-6"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                생성 중...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                전체 생성
              </>
            )}
          </Button>

          {completedScenes.size > 0 && (
            <Button
              onClick={downloadAllImages}
              variant="outline"
              size="lg"
            >
              <Download className="w-4 h-4 mr-2" />
              다운로드 ({completedScenes.size})
            </Button>
          )}
        </div>
      </div>

      {/* 진행률 표시 */}
      {(isGenerating || completedScenes.size > 0) && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">전체 진행률</span>
              <span className="text-sm text-gray-600">
                {completedScenes.size}/{scenes.length} 완료
              </span>
            </div>
            <Progress value={completionPercentage} className="h-2" />
          </CardContent>
        </Card>
      )}

      {/* 오류 메시지 */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 씬 목록 */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {scenes.map((scene) => {
          const isGenerating = generatingScenes.has(scene.id);
          const isCompleted = completedScenes.has(scene.id);
          const imageUrl = generatedImages[scene.id] || scene.preview_image_url;

          return (
            <Card key={scene.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">
                    씬 {scene.order}: {scene.title}
                  </CardTitle>
                  <div className="flex items-center space-x-1">
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${getSceneTypeColor(scene.scene_type)}`}
                    >
                      {getSceneTypeLabel(scene.scene_type)}
                    </Badge>
                    {isCompleted && (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    )}
                  </div>
                </div>
                <CardDescription className="text-xs">
                  {scene.description}
                </CardDescription>
              </CardHeader>

              <CardContent className="pt-0">
                {/* 이미지 영역 */}
                <div className="aspect-video bg-gray-100 rounded-lg mb-3 overflow-hidden relative">
                  {imageUrl ? (
                    <img
                      src={imageUrl}
                      alt={`${scene.title} 스토리보드`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        <Image className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">스토리보드 미생성</p>
                      </div>
                    </div>
                  )}

                  {isGenerating && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                      <div className="text-center text-white">
                        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                        <p className="text-sm">생성 중...</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* 씬 정보 */}
                <div className="flex items-center justify-between text-xs text-gray-600 mb-3">
                  <span className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {scene.duration}초
                  </span>
                </div>

                {/* 액션 버튼 */}
                <div className="flex space-x-2">
                  <Button
                    onClick={() => generateSceneStoryboard(scene.id)}
                    disabled={isGenerating}
                    size="sm"
                    variant={imageUrl ? "outline" : "default"}
                    className="flex-1 text-xs"
                  >
                    {isGenerating ? (
                      <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                    ) : imageUrl ? (
                      <RefreshCw className="w-3 h-3 mr-1" />
                    ) : (
                      <Image className="w-3 h-3 mr-1" />
                    )}
                    {imageUrl ? '재생성' : '생성'}
                  </Button>

                  {imageUrl && (
                    <Button
                      onClick={() => window.open(imageUrl, '_blank')}
                      size="sm"
                      variant="ghost"
                      className="text-xs"
                    >
                      <Eye className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 빈 상태 */}
      {scenes.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Image className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              씬이 없습니다
            </h3>
            <p className="text-gray-500">
              스토리보드를 생성하려면 먼저 스토리에 씬을 추가해주세요.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};