'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Sparkles, FileText, Image, Download, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface ProjectSettings {
  genre: string;
  tone: string;
  intensity: number;
  target_audience: string;
  key_message?: string;
  brand_values?: string[];
}

interface ProjectAnalysis {
  project_completeness: number;
  story_readiness: boolean;
  missing_elements: string[];
  recommendations: string[];
}

interface StoryStructure {
  act1_opening: string;
  act2_development: string;
  act3_climax: string;
  act4_resolution: string;
  overall_theme: string;
}

interface ScenePrompt {
  scene_number: number;
  act: string;
  title: string;
  description: string;
  visual_prompt: string;
  duration: number;
  scene_type: string;
}

interface StoryDevelopmentProps {
  projectId: string;
  onStoryDeveloped?: (storyData: any) => void;
  onStoryboardGenerated?: (storyboardData: any) => void;
  onPDFGenerated?: (pdfUrl: string) => void;
}

export const StoryDevelopment: React.FC<StoryDevelopmentProps> = ({
  projectId,
  onStoryDeveloped,
  onStoryboardGenerated,
  onPDFGenerated
}) => {
  const [activeTab, setActiveTab] = useState('analysis');
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<ProjectAnalysis | null>(null);
  const [storyStructure, setStoryStructure] = useState<StoryStructure | null>(null);
  const [scenePrompts, setScenePrompts] = useState<ScenePrompt[]>([]);
  const [storyboardUrls, setStoryboardUrls] = useState<Record<string, string>>({});
  const [pdfUrl, setPdfUrl] = useState<string>('');
  const [currentProject, setCurrentProject] = useState<ProjectSettings | null>(null);

  // 프로젝트 설정 분석
  const analyzeProject = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/ai-video/story-development/analyze-project/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_id: projectId }),
      });
      
      const data = await response.json();
      if (data.analysis) {
        setAnalysis(data.analysis);
        setCurrentProject(data.current_settings);
      }
    } catch (error) {
      console.error('프로젝트 분석 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 스토리 개요 생성
  const generateStoryOutline = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/ai-video/story-development/generate-story-outline/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_id: projectId }),
      });
      
      const data = await response.json();
      if (data.outline?.success) {
        setStoryStructure(data.outline.story_structure);
        setScenePrompts(data.outline.scene_prompts);
        onStoryDeveloped?.(data.outline);
        setActiveTab('story');
      }
    } catch (error) {
      console.error('스토리 생성 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 스토리보드 생성
  const generateStoryboard = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/ai-video/stories/${projectId}/generate-storyboard/`, {
        method: 'POST',
      });
      
      const data = await response.json();
      if (data.storyboard_urls) {
        const urlMap: Record<string, string> = {};
        data.storyboard_urls.forEach((item: any) => {
          if (item.preview_url) {
            urlMap[item.scene_number] = item.preview_url;
          }
        });
        setStoryboardUrls(urlMap);
        onStoryboardGenerated?.(data);
        setActiveTab('storyboard');
      }
    } catch (error) {
      console.error('스토리보드 생성 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // PDF 기획안 생성
  const generatePDFBrief = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/ai-video/stories/${projectId}/generate-pdf-brief/`, {
        method: 'POST',
      });
      
      const data = await response.json();
      if (data.pdf_url) {
        setPdfUrl(data.pdf_url);
        onPDFGenerated?.(data.pdf_url);
        setActiveTab('pdf');
      }
    } catch (error) {
      console.error('PDF 생성 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      analyzeProject();
    }
  }, [projectId]);

  const getIntensityLabel = (intensity: number) => {
    if (intensity <= 3) return '차분함';
    if (intensity <= 6) return '보통';
    if (intensity <= 8) return '활동적';
    return '매우 역동적';
  };

  const getCompletenessColor = (percentage: number) => {
    if (percentage >= 75) return 'text-green-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* 헤더 */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI 영상 기획 고도화
        </h1>
        <p className="text-gray-600">
          프로젝트 설정에 기반한 지능형 스토리 개발, 콘티 생성, PDF 기획안 제작
        </p>
      </div>

      {/* 진행 단계 표시 */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 ${analysis ? 'text-green-600' : 'text-gray-400'}`}>
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">프로젝트 분석</span>
          </div>
          <div className="w-8 h-px bg-gray-300" />
          <div className={`flex items-center space-x-2 ${storyStructure ? 'text-green-600' : 'text-gray-400'}`}>
            <Sparkles className="w-5 h-5" />
            <span className="font-medium">스토리 개발</span>
          </div>
          <div className="w-8 h-px bg-gray-300" />
          <div className={`flex items-center space-x-2 ${Object.keys(storyboardUrls).length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
            <Image className="w-5 h-5" />
            <span className="font-medium">콘티 생성</span>
          </div>
          <div className="w-8 h-px bg-gray-300" />
          <div className={`flex items-center space-x-2 ${pdfUrl ? 'text-green-600' : 'text-gray-400'}`}>
            <FileText className="w-5 h-5" />
            <span className="font-medium">PDF 제작</span>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="analysis">프로젝트 분석</TabsTrigger>
          <TabsTrigger value="story">스토리 구조</TabsTrigger>
          <TabsTrigger value="storyboard">콘티 생성</TabsTrigger>
          <TabsTrigger value="pdf">PDF 기획안</TabsTrigger>
        </TabsList>

        {/* 프로젝트 분석 탭 */}
        <TabsContent value="analysis" className="space-y-6">
          {analysis ? (
            <div className="grid gap-6 md:grid-cols-2">
              {/* 프로젝트 완성도 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5" />
                    <span>프로젝트 완성도</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className={`text-4xl font-bold ${getCompletenessColor(analysis.project_completeness)}`}>
                      {Math.round(analysis.project_completeness)}%
                    </div>
                    <Progress value={analysis.project_completeness} className="mt-2" />
                  </div>
                  
                  <Badge variant={analysis.story_readiness ? 'default' : 'secondary'} className="w-full justify-center">
                    {analysis.story_readiness ? '스토리 개발 준비 완료' : '추가 설정 필요'}
                  </Badge>

                  {analysis.missing_elements.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">누락된 설정</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.missing_elements.map((element) => (
                          <Badge key={element} variant="outline" className="text-red-600">
                            {element}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* 현재 설정 */}
              {currentProject && (
                <Card>
                  <CardHeader>
                    <CardTitle>현재 프로젝트 설정</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">장르:</span>
                        <span className="ml-2 font-medium">{currentProject.genre}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">톤:</span>
                        <span className="ml-2 font-medium">{currentProject.tone}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">강도:</span>
                        <span className="ml-2 font-medium">
                          {currentProject.intensity} - {getIntensityLabel(currentProject.intensity)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">타겟:</span>
                        <span className="ml-2 font-medium">{currentProject.target_audience}</span>
                      </div>
                    </div>

                    {currentProject.key_message && (
                      <div>
                        <span className="text-gray-600 block text-sm">핵심 메시지:</span>
                        <p className="text-sm mt-1">{currentProject.key_message}</p>
                      </div>
                    )}

                    {currentProject.brand_values && currentProject.brand_values.length > 0 && (
                      <div>
                        <span className="text-gray-600 block text-sm mb-2">브랜드 가치:</span>
                        <div className="flex flex-wrap gap-1">
                          {currentProject.brand_values.map((value) => (
                            <Badge key={value} variant="outline" className="text-xs">
                              {value}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* 추천사항 */}
              {analysis.recommendations.length > 0 && (
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <AlertCircle className="w-5 h-5 text-amber-500" />
                      <span>추천사항</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {analysis.recommendations.map((recommendation, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-2 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
              <p>프로젝트를 분석 중입니다...</p>
            </div>
          )}

          <div className="flex justify-center">
            <Button
              onClick={generateStoryOutline}
              disabled={!analysis?.story_readiness || isLoading}
              size="lg"
              className="px-8"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  생성 중...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  스토리 개발 시작
                </>
              )}
            </Button>
          </div>
        </TabsContent>

        {/* 스토리 구조 탭 */}
        <TabsContent value="story" className="space-y-6">
          {storyStructure ? (
            <div className="space-y-6">
              {/* 전체 테마 */}
              <Card>
                <CardHeader>
                  <CardTitle>전체 스토리 테마</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700">{storyStructure.overall_theme}</p>
                </CardContent>
              </Card>

              {/* 4막 구조 */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">1막: 오프닝</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{storyStructure.act1_opening}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">2막: 전개</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{storyStructure.act2_development}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">3막: 클라이맥스</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{storyStructure.act3_climax}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">4막: 결말</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{storyStructure.act4_resolution}</p>
                  </CardContent>
                </Card>
              </div>

              {/* 씬별 상세 */}
              <Card>
                <CardHeader>
                  <CardTitle>씬별 상세 구성 (총 {scenePrompts.length}개)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {scenePrompts.map((scene) => (
                      <div key={scene.scene_number} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">
                            씬 {scene.scene_number}: {scene.title}
                          </h4>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">{scene.act}</Badge>
                            <Badge variant="secondary">{scene.scene_type}</Badge>
                            <span className="text-xs text-gray-500">{scene.duration}초</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{scene.description}</p>
                        <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                          <strong>비주얼 프롬프트:</strong> {scene.visual_prompt}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="flex justify-center">
                <Button
                  onClick={generateStoryboard}
                  disabled={isLoading}
                  size="lg"
                  className="px-8"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      생성 중...
                    </>
                  ) : (
                    <>
                      <Image className="w-4 h-4 mr-2" />
                      콘티 생성하기
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">스토리 개발을 먼저 진행해주세요.</p>
            </div>
          )}
        </TabsContent>

        {/* 스토리보드 탭 */}
        <TabsContent value="storyboard" className="space-y-6">
          {Object.keys(storyboardUrls).length > 0 ? (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold mb-2">생성된 스토리보드</h3>
                <p className="text-gray-600">총 {Object.keys(storyboardUrls).length}개의 씬 이미지가 생성되었습니다.</p>
              </div>

              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Object.entries(storyboardUrls).map(([sceneNumber, imageUrl]) => {
                  const scene = scenePrompts.find(s => s.scene_number === parseInt(sceneNumber));
                  return (
                    <Card key={sceneNumber}>
                      <CardContent className="p-4">
                        <div className="aspect-video bg-gray-100 rounded-lg mb-3 overflow-hidden">
                          <img
                            src={imageUrl}
                            alt={`Scene ${sceneNumber}`}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div className="text-center">
                          <h4 className="font-medium text-sm">
                            씬 {sceneNumber}: {scene?.title || '제목 없음'}
                          </h4>
                          <p className="text-xs text-gray-500 mt-1">
                            {scene?.duration}초 • {scene?.act}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              <div className="flex justify-center">
                <Button
                  onClick={generatePDFBrief}
                  disabled={isLoading}
                  size="lg"
                  className="px-8"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      생성 중...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4 mr-2" />
                      PDF 기획안 제작
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">콘티 생성을 먼저 진행해주세요.</p>
            </div>
          )}
        </TabsContent>

        {/* PDF 기획안 탭 */}
        <TabsContent value="pdf" className="space-y-6">
          {pdfUrl ? (
            <div className="text-center space-y-6">
              <div>
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">PDF 기획안 제작 완료</h3>
                <p className="text-gray-600">
                  프로젝트 설정, 스토리 구조, 콘티, 인서트샷을 포함한 완전한 기획안이 준비되었습니다.
                </p>
              </div>

              <div className="max-w-md mx-auto">
                <Card>
                  <CardContent className="p-6 text-center">
                    <FileText className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                    <h4 className="font-medium mb-2">VideoPlanet 프로젝트 기획안</h4>
                    <p className="text-sm text-gray-500 mb-4">
                      전체 {scenePrompts.length}페이지 • PDF 형식
                    </p>
                    <Button
                      onClick={() => window.open(pdfUrl, '_blank')}
                      className="w-full"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      기획안 다운로드
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">PDF 기획안 제작을 먼저 진행해주세요.</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};