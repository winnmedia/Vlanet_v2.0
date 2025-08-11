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
        setError(data.error || 'PDF    .');
      }
    } catch (err) {
      setError('  .');
      console.error('PDF  :', err);
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
      // PDF   (: PDF.js)
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
      {/*  */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">PDF  </h2>
        <p className="text-gray-600">
              PDF 
        </p>
      </div>

      {/*   */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg"> </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <FileText className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-blue-700">{storyTitle}</div>
              <div className="text-sm text-blue-600"> </div>
            </div>

            <div className="text-center p-4 bg-green-50 rounded-lg">
              <ImageIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-green-700">{sceneCount}</div>
              <div className="text-sm text-green-600">  </div>
            </div>

            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Clock className="w-8 h-8 text-purple-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-purple-700">{formatDuration(totalDuration)}</div>
              <div className="text-sm text-purple-600">  </div>
            </div>

            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <Calendar className="w-8 h-8 text-orange-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-orange-700">{new Date().toLocaleDateString('ko-KR')}</div>
              <div className="text-sm text-orange-600"> </div>
            </div>
          </div>

          {projectName && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">:</span>
              <span className="ml-2 text-sm text-gray-900">{projectName}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* PDF   */}
      <Card>
        <CardHeader>
          <CardTitle>  </CardTitle>
          <CardDescription>
                PDF  
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm"> </div>
                <div className="text-xs text-gray-600">, ,  </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm"> </div>
                <div className="text-xs text-gray-600">4 ,  </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm"> </div>
                <div className="text-xs text-gray-600">   </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm"> </div>
                <div className="text-xs text-gray-600">  </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm"> </div>
                <div className="text-xs text-gray-600">, FPS, </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <div>
                <div className="font-medium text-sm">  </div>
                <div className="text-xs text-gray-600">  </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/*   */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/*     */}
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
                PDF  ...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5 mr-2" />
                PDF  
              </>
            )}
          </Button>

          {isGenerating && (
            <div className="mt-4 text-sm text-gray-600">
              <p>PDF  1-2    .</p>
              <p> ...</p>
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
                  PDF   !
                </h3>
                <p className="text-green-700">
                  {generatedPDF.content_summary.total_pages}   .
                </p>
              </div>

              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex items-center justify-center space-x-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{generatedPDF.content_summary.total_pages}</div>
                    <div className="text-sm text-gray-600"> </div>
                  </div>
                  <div className="w-px h-8 bg-gray-300" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{generatedPDF.content_summary.sections.length}</div>
                    <div className="text-sm text-gray-600"> </div>
                  </div>
                  <div className="w-px h-8 bg-gray-300" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{generatedPDF.content_summary.scene_count}</div>
                    <div className="text-sm text-gray-600"> </div>
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
                  
                </Button>
                <Button onClick={downloadPDF} size="lg" className="bg-green-600 hover:bg-green-700">
                  <Download className="w-4 h-4 mr-2" />
                  
                </Button>
              </div>

              <div className="text-sm text-green-600">
                : {generatedPDF.filename}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};