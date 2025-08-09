'use client';

import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, FileText, Download, CheckCircle, AlertCircle, Eye, Calendar, Clock, Image as ImageIcon } from 'lucide-react';

interface PDFGeneratorProps {
  storyId: string;
  storyTitle: string;
  projectName?: string;
  sceneCount: number;
  totalDuration: number;
  onPDFGenerated?: (pdfUrl: string, filename: string) => void;
}

interface GeneratedPDF {
  pdf_url: string;
  filename: string;
  content_summary: {
    total_pages: number;
    sections: string[];
    scene_count: number;
  };
}

export const PDFGenerator: React.FC<PDFGeneratorProps> = ({
  storyId,
  storyTitle,
  projectName,
  sceneCount,
  totalDuration,
  onPDFGenerated
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPDF, setGeneratedPDF] = useState<GeneratedPDF | null>(null);
  const [error, setError] = useState<string>('');

  const generatePDF = useCallback(async () => {
    if (!storyId) return;

    setIsGenerating(true);
    setError('');

    try {
      const response = await fetch(`/api/ai-video/stories/${storyId}/generate-pdf-brief/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      
      if (response.ok && data.pdf_url) {
        const pdfData: GeneratedPDF = {
          pdf_url: data.pdf_url,
          filename: data.filename,
          content_summary: data.content_summary
        };
        
        setGeneratedPDF(pdfData);
        onPDFGenerated?.(data.pdf_url, data.filename);
      } else {
        setError(data.error || 'PDF 생성 중 오류가 발생했습니다.');
      }
    } catch (err) {
      setError('네트워크 오류가 발생했습니다.');
      console.error('PDF 생성 오류:', err);
    } finally {
      setIsGenerating(false);
    }
  }, [storyId, onPDFGenerated]);

  const downloadPDF = useCallback(() => {
    if (generatedPDF?.pdf_url) {
      window.open(generatedPDF.pdf_url, '_blank');
    }
  }, [generatedPDF]);

  const previewPDF = useCallback(() => {
    if (generatedPDF?.pdf_url) {
      // PDF 뷰어로 미리보기 (예: PDF.js)
      window.open(`/pdf-viewer?url=${encodeURIComponent(generatedPDF.pdf_url)}`, '_blank');
    }
  }, [generatedPDF]);

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">PDF 기획안 생성</h2>
        <p className="text-gray-600">
          완전한 영상 제작 기획안을 PDF로 생성합니다
        </p>
      </div>

      {/* 프로젝트 정보 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">프로젝트 개요</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <FileText className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-blue-700">{storyTitle}</div>
              <div className="text-sm text-blue-600">스토리 제목</div>
            </div>

            <div className="text-center p-4 bg-green-50 rounded-lg">
              <ImageIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-green-700">{sceneCount}</div>
              <div className="text-sm text-green-600">총 씬 개수</div>
            </div>

            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Clock className="w-8 h-8 text-purple-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-purple-700">{formatDuration(totalDuration)}</div>
              <div className="text-sm text-purple-600">총 영상 길이</div>
            </div>

            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <Calendar className="w-8 h-8 text-orange-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-orange-700">{new Date().toLocaleDateString('ko-KR')}</div>
              <div className="text-sm text-orange-600">생성 날짜</div>
            </div>
          </div>

          {projectName && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">프로젝트:</span>
              <span className="ml-2 text-sm text-gray-900">{projectName}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* PDF 생성 섹션 */}
      <Card>
        <CardHeader>
          <CardTitle>기획안 구성 요소</CardTitle>
          <CardDescription>
            다음 내용들이 포함된 완전한 PDF 기획안을 생성합니다
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">프로젝트 개요</div>
                <div className="text-xs text-gray-600">제목, 설명, 기본 설정</div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">스토리 구조</div>
                <div className="text-xs text-gray-600">4막 구조, 전체 테마</div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">씬별 상세</div>
                <div className="text-xs text-gray-600">각 씬의 설명과 프롬프트</div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">스토리보드 이미지</div>
                <div className="text-xs text-gray-600">생성된 콘티 이미지</div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">기술적 사양</div>
                <div className="text-xs text-gray-600">해상도, FPS, 포맷</div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">인서트 샷 추천</div>
                <div className="text-xs text-gray-600">추가 촬영 가이드</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 오류 메시지 */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 생성 버튼 또는 결과 */}
      {!generatedPDF ? (
        <div className="text-center">
          <Button
            onClick={generatePDF}
            disabled={isGenerating}
            size="lg"
            className="px-8"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                PDF 생성 중...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5 mr-2" />
                PDF 기획안 생성
              </>
            )}
          </Button>

          {isGenerating && (
            <div className="mt-4 text-sm text-gray-600">
              <p>PDF 생성에는 1-2분 정도 소요될 수 있습니다.</p>
              <p>잠시만 기다려주세요...</p>
            </div>
          )}
        </div>
      ) : (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="p-6">
            <div className="text-center space-y-4">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              
              <div>
                <h3 className="text-xl font-semibold text-green-800 mb-2">
                  PDF 기획안 생성 완료!
                </h3>
                <p className="text-green-700">
                  {generatedPDF.content_summary.total_pages}페이지의 완전한 기획안이 준비되었습니다.
                </p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex items-center justify-center space-x-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{generatedPDF.content_summary.total_pages}</div>
                    <div className="text-sm text-gray-600">총 페이지</div>
                  </div>
                  <div className="w-px h-8 bg-gray-300" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{generatedPDF.content_summary.sections.length}</div>
                    <div className="text-sm text-gray-600">구성 섹션</div>
                  </div>
                  <div className="w-px h-8 bg-gray-300" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{generatedPDF.content_summary.scene_count}</div>
                    <div className="text-sm text-gray-600">포함 씬</div>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap justify-center gap-2">
                {generatedPDF.content_summary.sections.map((section, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {section}
                  </Badge>
                ))}
              </div>

              <div className="flex justify-center space-x-3">
                <Button onClick={previewPDF} variant="outline" size="lg">
                  <Eye className="w-4 h-4 mr-2" />
                  미리보기
                </Button>
                <Button onClick={downloadPDF} size="lg" className="bg-green-600 hover:bg-green-700">
                  <Download className="w-4 h-4 mr-2" />
                  다운로드
                </Button>
              </div>

              <div className="text-sm text-green-600">
                파일명: {generatedPDF.filename}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};