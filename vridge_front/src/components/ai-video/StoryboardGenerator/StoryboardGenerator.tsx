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

  //   
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
        setError(data.error || '    .');
      }
    } catch (err) {
      setError('  .');
      console.error('  :', err);
    } finally {
      setIsGenerating(false);
    }
  }, [storyId, scenes, onStoryboardGenerated]);

  //    
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
        setError(data.error || ` ${sceneId}   `);
      }
    } catch (err) {
      setError('  .');
      console.error('   :', err);
    } finally {
      setGeneratingScenes(prev => {
        const next = new Set(prev);
        next.delete(sceneId);
        return next;
      });
    }
  }, [generatingScenes, onSceneUpdated]);

  //    (ZIP)
  const downloadAllImages = useCallback(async () => {
    const imageUrls = Object.values(generatedImages).filter(Boolean);
    
    if (imageUrls.length === 0) {
      setError('  .');
      return;
    }

    try {
      //   ZIP  API 
      //   ZIP   
      alert(`${imageUrls.length}   .`);
    } catch (err) {
      setError('   .');
      console.error(' :', err);
    }
  }, [generatedImages]);

  const getSceneTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      intro: '',
      main: '',
      transition: '',
      outro: '',
      text_overlay: '',
      b_roll: 'B'
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
      {/*     */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900"> </h2>
          <p className="text-gray-600 mt-1">
            AI      
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
                 ...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                 
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
               ({completedScenes.size})
            </Button>
          )}
        </div>
      </div>

      {/*   */}
      {(isGenerating || completedScenes.size > 0) && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium"> </span>
              <span className="text-sm text-gray-600">
                {completedScenes.size}/{scenes.length} 
              </span>
            </div>
            <Progress value={completionPercentage} className="h-2" />
          </CardContent>
        </Card>
      )}

      {/*   */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/*   */}
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
                     {scene.order}: {scene.title}
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
                {/*   */}
                <div className="aspect-video bg-gray-100 rounded-lg mb-3 overflow-hidden relative">
                  {imageUrl ? (
                    <img
                      src={imageUrl}
                      alt={`${scene.title} `}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        <Image className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500"> </p>
                      </div>
                    </div>
                  )}

                  {isGenerating && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                      <div className="text-center text-white">
                        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
                        <p className="text-sm"> ...</p>
                      </div>
                    </div>
                  )}
                </div>

                {/*   */}
                <div className="flex items-center justify-between text-xs text-gray-600 mb-3">
                  <span className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {scene.duration}
                  </span>
                </div>

                {/*   */}
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
                    {imageUrl ? '' : ''}
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

      {/*   */}
      {scenes.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Image className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
               
            </h3>
            <p className="text-gray-500">
                   .
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};